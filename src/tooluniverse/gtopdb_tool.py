import re
import requests
from typing import Any, Dict
from .base_tool import BaseTool
from .http_utils import request_with_retry
from .tool_registry import register_tool


def _strip_html(text: Any) -> Any:
    """Strip HTML tags and decode HTML entities from a string.

    BUG-49A-H3: GtoPdb returns raw HTML tags in some fields (e.g., <sup>, <i>).
    BUG-51B-002: GtoPdb also returns HTML entities (e.g., &ouml; → ö, &alpha; → α).
    """
    if not isinstance(text, str):
        return text
    # First strip tags, then decode entities
    stripped = re.sub(r"<[^>]+>", "", text).strip()
    # Decode common HTML entities
    import html

    return html.unescape(stripped)


# BUG-53A-005: HGNC gene symbols → GtoPdb pharmacological receptor/enzyme names.
# GtoPdb indexes nuclear receptors and GPCRs by pharmacological names (ERα, D2 receptor)
# not HGNC gene symbols (ESR1, DRD2). When gene_symbol lookup returns 404, fall back to
# searching by the pharmacological name from this mapping.
_HGNC_TO_GTOPDB_NAME: dict = {
    "ESR1": "ERα",
    "ESR2": "ERβ",
    "AR": "androgen receptor",
    "PPARG": "PPARγ",
    "PPARA": "PPARα",
    "PPARD": "PPARδ",
    "NR3C1": "glucocorticoid receptor",
    "NR3C2": "mineralocorticoid receptor",
    "NR1I2": "pregnane X receptor",
    "VDR": "vitamin D receptor",
    "RXRA": "RXRα",
    "DRD1": "D1 receptor",
    "DRD2": "D2 receptor",
    "DRD3": "D3 receptor",
    "DRD4": "D4 receptor",
    "DRD5": "D5 receptor",
    "HTR1A": "5-HT1A receptor",
    "HTR2A": "5-HT2A receptor",
    "ADRB1": "β1-adrenoceptor",
    "ADRB2": "β2-adrenoceptor",
    "ADRA1A": "α1A-adrenoceptor",
    "CHRM1": "M1 receptor",
    "CHRM2": "M2 receptor",
    "CHRM3": "M3 receptor",
    "OPRD1": "δ receptor",
    "OPRM1": "μ receptor",
    "OPRK1": "κ receptor",
    "PTGER2": "EP2 receptor",
    "PTGER4": "EP4 receptor",
    "HDAC1": "HDAC1",
    "PARP1": "PARP1",
}


@register_tool("GtoPdbRESTTool")
class GtoPdbRESTTool(BaseTool):
    def __init__(self, tool_config: Dict):
        super().__init__(tool_config)
        self.base_url = "https://www.guidetopharmacology.org/services"
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.timeout = 30

    def _build_url(self, args: Dict[str, Any]) -> str:
        """Build URL with path parameters and query parameters."""
        url = self.tool_config["fields"]["endpoint"]

        # BUG-29A-07 fix: interactions endpoint requires path params, not query params
        # /services/interactions?targetId=X is ignored; must use /targets/{id}/interactions
        if (
            url.endswith("/interactions")
            and "{targetId}" not in url
            and "{ligandId}" not in url
        ):
            # Accept both camelCase and snake_case aliases
            target_id = args.get("targetId") or args.get("target_id")
            ligand_id = args.get("ligandId") or args.get("ligand_id")
            if target_id is not None:
                url = f"{self.base_url}/targets/{target_id}/interactions"
                # BUG-53A-002: when BOTH targetId AND ligandId are provided, the original code
                # only used targetId (correct for URL construction) but also silently removed
                # ligandId from args without setting _pending_ligand_id_filter. This meant the
                # client-side ligandId filter (set up in the elif branch) never ran, so the
                # ligandId parameter was completely ignored. Fix: preserve ligandId for
                # client-side filtering when both are provided.
                if ligand_id is not None:
                    self._pending_ligand_id_filter = ligand_id
                args = {
                    k: v
                    for k, v in args.items()
                    if k not in ("targetId", "target_id", "ligandId", "ligand_id")
                }
            elif ligand_id is not None:
                # BUG-38B-02: /ligands/{id}/interactions always returns [] per GtoPdb REST API.
                # GtoPdb interactions are indexed by TARGET. Store ligand_id on self for use in run().
                self._pending_ligand_id_filter = ligand_id
                # Fall back to main interactions endpoint; run() will filter client-side
                url = f"{self.base_url}/interactions"
                args = {
                    k: v
                    for k, v in args.items()
                    if k not in ("targetId", "target_id", "ligandId", "ligand_id")
                }

        query_params = {}

        # Separate path params from query params
        path_params = {}
        for k, v in args.items():
            if f"{{{k}}}" in url:
                # This is a path parameter
                path_params[k] = v
            else:
                # This is a query parameter
                query_params[k] = v

        # Replace path parameters in URL
        for k, v in path_params.items():
            url = url.replace(f"{{{k}}}", str(v))

        # Build query string for remaining parameters
        if query_params:
            # Map parameter names to GtoPdb API parameter names
            param_mapping = {
                "target_type": "type",
                "ligand_type": "type",
                "action_type": "type",
                "affinity_parameter": "affinityParameter",
                "min_affinity": "affinity",
                "approved_only": "approved",
                "query": "name",  # alias: query → name (GtoPdb API uses ?name=)
            }

            api_params = {}
            for k, v in query_params.items():
                # Skip limit as it's handled separately
                if k == "limit":
                    continue
                # Map parameter name
                api_key = param_mapping.get(k, k)
                # Convert boolean to lowercase string for API
                if isinstance(v, bool):
                    v = str(v).lower()
                api_params[api_key] = v

            # Build query string
            if api_params:
                from urllib.parse import urlencode

                url = f"{url}?{urlencode(api_params)}"

        return url

    def _search_targets_by_abbreviation_variants(self, query: str, limit: int) -> list:
        """BUG-44A-04: When name search returns results whose names don't contain the query
        (e.g., 'PARP' → tankyrase via PARP5 synonym), also search for numbered variants
        like PARP1, PARP2, PARP3 and merge results.

        GtoPdb stores PARPs under full names ('poly(ADP-ribose) polymerase 1') but
        the abbreviation field has 'PARP1'. The API name= parameter matches abbreviations,
        so name=PARP1 finds the right target.
        """
        results = []
        seen_ids: set = set()
        from urllib.parse import urlencode

        # Try numbered variants: PARP1, PARP2, ..., PARP9
        for suffix in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
            if len(results) >= limit:
                break
            candidate = f"{query}{suffix}"
            try:
                url = f"{self.base_url}/targets?{urlencode({'name': candidate})}"
                response = request_with_retry(
                    self.session, "GET", url, timeout=self.timeout, max_attempts=1
                )
                if response.status_code == 200:
                    for t in response.json():
                        tid = t.get("targetId")
                        if tid and tid not in seen_ids:
                            seen_ids.add(tid)
                            results.append(t)
            except Exception:
                pass
        return results[:limit]

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        url = None
        self._pending_ligand_id_filter = None  # BUG-38B-02: reset per call

        # BUG-46A-04: gene_symbol convenience parameter for GtoPdb_get_interactions.
        # Auto-resolve gene symbol → targetId so users don't need a separate
        # GtoPdb_search_targets call before querying interactions.
        gene_symbol = arguments.get("gene_symbol")
        if (
            gene_symbol
            and not arguments.get("targetId")
            and not arguments.get("target_id")
        ):
            from urllib.parse import urlencode

            lookup_url = f"{self.base_url}/targets?{urlencode({'name': gene_symbol})}"
            try:
                resp = request_with_retry(
                    self.session,
                    "GET",
                    lookup_url,
                    timeout=self.timeout,
                    max_attempts=2,
                )
                # BUG-52B-002: GtoPdb returns HTTP 404 (not 200) when a gene_symbol
                # doesn't match any target name. Previously, resp.status_code != 200
                # caused the entire lookup block to be skipped silently, leaving
                # gene_symbol in arguments → _build_url adds it as an unknown query
                # param → API ignores it → returns ALL interactions (e.g., 5-HT1A
                # receptor data for gene_symbol="MAP2K1"). Fix: handle 404 by returning
                # early with a helpful message, and validate list type on 200.
                if resp.status_code == 404 or (
                    resp.status_code == 200 and not isinstance(resp.json(), list)
                ):
                    # BUG-53A-005: some HGNC gene symbols map to GtoPdb pharmacological
                    # receptor names (e.g., ESR1 → "ERα", DRD2 → "D2 receptor").
                    # Try a fallback lookup using the known pharmacological name.
                    fallback_resolved = False
                    gtopdb_name = _HGNC_TO_GTOPDB_NAME.get(gene_symbol.upper())
                    if gtopdb_name:
                        try:
                            from urllib.parse import urlencode as _urlencode

                            fb_url = f"{self.base_url}/targets?{_urlencode({'name': gtopdb_name})}"
                            fb_resp = request_with_retry(
                                self.session,
                                "GET",
                                fb_url,
                                timeout=self.timeout,
                                max_attempts=2,
                            )
                            if fb_resp.status_code == 200:
                                fb_targets = fb_resp.json()
                                if isinstance(fb_targets, list) and fb_targets:
                                    target_id = fb_targets[0]["targetId"]
                                    arguments = dict(arguments)
                                    arguments["targetId"] = target_id
                                    arguments.pop("gene_symbol", None)
                                    fallback_resolved = True
                        except Exception:
                            pass
                    if not fallback_resolved:
                        return {
                            "status": "success",
                            "data": [],
                            "count": 0,
                            "message": (
                                f"No GtoPdb target found for gene_symbol='{gene_symbol}'. "
                                "GtoPdb targets are indexed by pharmacological receptor/enzyme "
                                "names and may not recognize all HGNC gene symbols. "
                                f"Try GtoPdb_search_targets with a descriptive name "
                                f"(e.g., query='MEK1' or 'MAP2K1' or 'MEK' for MAP2K1). "
                                "Nuclear receptors use Greek-letter names (ESR1→'ERα', "
                                "AR→'androgen receptor', PPARG→'PPARγ'). "
                                "Note: many kinases and signaling enzymes (MAP2K1/MEK1, "
                                "MAP2K2/MEK2, MAPK1/ERK2, MAPK3/ERK1, etc.) have limited "
                                "or no interaction data in GtoPdb — use "
                                "ChEMBL_get_drug_mechanisms or ChEMBL_search_compounds "
                                "for approved inhibitors of MAP kinase pathway proteins."
                            ),
                        }
                if resp.status_code == 200:
                    targets = resp.json()
                    if isinstance(targets, list) and targets:
                        # Prefer exact abbreviation match (e.g., "KRAS" → KRAS entry)
                        gene_upper = gene_symbol.upper()
                        target_id = None
                        for t in targets:
                            if (t.get("abbreviation") or "").upper() == gene_upper:
                                target_id = t["targetId"]
                                break
                        # BUG-48A-05: before falling back to targets[0], try prefix match.
                        # e.g., gene_symbol="ABL1", abbreviation="Abl" →
                        # "abl1".startswith("abl") with rest "1" being a digit → ABL1 selected.
                        # This prevents "ABL1" from silently returning ABL2 (abbr "Arg").
                        if target_id is None:
                            gene_lower = gene_symbol.lower()
                            best_match = None
                            best_len = 0
                            for t in targets:
                                abbr = (t.get("abbreviation") or "").lower()
                                if (
                                    abbr
                                    and gene_lower.startswith(abbr)
                                    and len(abbr) > best_len
                                ):
                                    rest = gene_lower[len(abbr) :]
                                    if rest == "" or rest.isdigit():
                                        best_match = t["targetId"]
                                        best_len = len(abbr)
                            if best_match is not None:
                                target_id = best_match
                        if target_id is None:
                            target_id = targets[0]["targetId"]
                        arguments = dict(arguments)
                        arguments["targetId"] = target_id
                        # BUG-47A-05: remove gene_symbol so it doesn't leak into the API URL
                        arguments.pop("gene_symbol", None)
            except Exception:
                pass

        try:
            url = self._build_url(arguments)
            response = request_with_retry(
                self.session, "GET", url, timeout=self.timeout, max_attempts=3
            )
            if response.status_code == 404 and "?" in url:
                # BUG-37A-02: on search endpoints (URL has query params), 404 means no results
                # not a real error. Provide helpful guidance.
                hint = ""
                if "/targets" in url:
                    hint = " If searching for a drug/ligand name, use GtoPdb_search_ligands instead."
                elif "/ligands" in url:
                    hint = " If searching for a target name, use GtoPdb_search_targets instead."
                return {
                    "status": "success",
                    "data": [],
                    "count": 0,
                    "url": url,
                    "message": f"No results found matching the search criteria.{hint}",
                }
            if response.status_code != 200:
                raw_detail = (response.text or "")[:500]
                # BUG-35A-01: extract human-readable API error from JSON detail
                try:
                    import json as _json

                    detail_obj = _json.loads(raw_detail)
                    api_msg = detail_obj.get("error", raw_detail)
                except Exception:
                    api_msg = raw_detail
                return {
                    "status": "error",
                    "error": f"GtoPdb API error: {api_msg} (HTTP {response.status_code})",
                    "url": url,
                    "status_code": response.status_code,
                    "detail": raw_detail,
                }
            data = response.json()

            # BUG-49A-H3: strip raw HTML tags from GtoPdb API fields.
            # GtoPdb returns HTML-formatted display values in some fields
            # (e.g., originalAffinity="6.3x10<sup>-6</sup>", ligandName="compound 5 [Smith <i>et al</i>., 2020]").
            # Strip tags so LLMs and downstream code receive plain text.
            _HTML_FIELDS = ("originalAffinity", "ligandName", "authors", "name")
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for field in _HTML_FIELDS:
                            if field in item:
                                item[field] = _strip_html(item[field])

            # BUG-38B-02: client-side filter by ligandId when requested
            # (/ligands/{id}/interactions always returns [], so we fetch all and filter)
            ligand_id_filter = getattr(self, "_pending_ligand_id_filter", None)
            if ligand_id_filter is not None and isinstance(data, list):
                data = [x for x in data if x.get("ligandId") == ligand_id_filter]

            # Apply limit if specified (max_results is an alias for limit)
            # BUG-47A-04: increased default from 20 to 50 — interaction-rich targets
            # like EGFR (90 interactions) would only show 22% of data at limit=20.
            limit = arguments.get("limit", arguments.get("max_results", 50))
            if isinstance(data, list) and len(data) > limit:
                data = data[:limit]

            result: Dict[str, Any] = {
                "status": "success",
                "data": data,
                "url": url,
                "count": len(data) if isinstance(data, list) else 1,
            }

            # BUG-38B-02: if ligandId filter returned nothing, add informative hint
            ligand_id_filter = getattr(self, "_pending_ligand_id_filter", None)
            if ligand_id_filter is not None and result["count"] == 0:
                result["message"] = (
                    f"No interactions found for ligandId={ligand_id_filter} in the GtoPdb "
                    "interactions database. Possible reasons: (1) The drug may be stored under "
                    "a related compound entry — some approved drugs (e.g., vemurafenib ID=5893) "
                    "have pharmacological data under their research compound record (e.g., ID=8548). "
                    "Check the ligand details from GtoPdb_search_ligands for 'activeDrugIds' or "
                    "'prodrugIds' fields and try those IDs. (2) The drug may not be in the GtoPdb "
                    "interactions database. GtoPdb covers GPCR, ion channel, enzyme, and transporter "
                    "interactions; some targets may be absent. Search by target_id instead if you "
                    "know the GtoPdb target ID."
                )

            # BUG-44A-04: for target name searches, detect when returned target names
            # don't contain the query string (meaning the match was via abbreviation/synonym,
            # e.g. name=PARP matches tankyrase via its PARP5 synonym). In that case,
            # also search for numbered variants (PARP1, PARP2, ...) and merge results.
            query = arguments.get("query")
            if (
                query
                and "/targets" in url
                and "/targets/" not in url
                and isinstance(data, list)
            ):
                q_lower = query.lower()
                # Check if the query appears in any returned target name
                names_contain_query = any(
                    q_lower in t.get("name", "").lower() for t in data
                )
                if not names_contain_query and data:
                    # The match was via synonym/abbreviation; try numbered variants
                    extra = self._search_targets_by_abbreviation_variants(query, limit)
                    if extra:
                        existing_ids = {t.get("targetId") for t in data}
                        new_targets = [
                            t for t in extra if t.get("targetId") not in existing_ids
                        ]
                        if new_targets:
                            data = new_targets + data  # put canonical matches first
                            result["data"] = data
                            result["count"] = len(data)
                            result["note"] = (
                                f"Searched for '{query}'. Results include targets with abbreviation "
                                f"matching '{query}' (e.g., {data[0].get('name', '')}) as well as "
                                f"targets matched via synonym. For kinase/enzyme families, try "
                                f"searching with full gene symbols like '{query}1', '{query}2'."
                            )

            # BUG-35A-02: add top-level queried_target summary for interactions endpoint
            # so users can immediately verify they're getting the right target's data
            if isinstance(data, list) and data and "/interactions" in url:
                first = data[0]
                if "targetId" in first or "targetName" in first:
                    result["queried_target"] = {
                        "id": first.get("targetId"),
                        "name": first.get("targetName"),
                    }
                elif "ligandId" in first or "ligandName" in first:
                    result["queried_ligand"] = {
                        "id": first.get("ligandId"),
                        "name": first.get("ligandName"),
                    }
                # BUG-49B-002: when no approved drugs are in the returned interactions,
                # add a coverage note. GtoPdb's kinase inhibitor and enzyme inhibitor
                # coverage is incomplete — approved drugs like imatinib (ABL1), olaparib
                # (PARP1), and erlotinib (EGFR) may be absent. Suggest ChEMBL for approved drugs.
                has_approved = any(
                    item.get("approved") for item in data if isinstance(item, dict)
                )
                if not has_approved and isinstance(data, list) and len(data) > 0:
                    result["coverage_note"] = (
                        "None of the returned interactions are for approved drugs. GtoPdb's "
                        "kinase inhibitor and enzyme inhibitor coverage may be incomplete — "
                        "approved drugs for this target may not be represented. For a complete "
                        "list of approved drugs and clinical compounds, use ChEMBL_get_drug_mechanisms "
                        "or ChEMBL_search_compounds with the target name."
                    )

            # BUG-49A-M5: for ligand search results, add a hint about getting interaction data.
            # BUG-51A-001: warn that ligandId-based lookups often fail for enzyme/kinase
            # inhibitors (PARP, HDAC, CDK, etc.) because GtoPdb indexes interactions by TARGET.
            # In those cases, querying by gene_symbol or targetId is more reliable.
            if isinstance(data, list) and data and "/ligands" in url and "?" in url:
                result["hint"] = (
                    "To find pharmacological interactions for a specific ligand, try "
                    "GtoPdb_get_interactions with ligandId=<id>. IMPORTANT: For enzyme "
                    "and kinase inhibitors (e.g., PARP inhibitors, CDK inhibitors, HDAC "
                    "inhibitors, kinase inhibitors), GtoPdb indexes interactions by TARGET, "
                    "and ligandId-based queries often return empty results even for approved "
                    "drugs. In that case, query by gene_symbol (e.g., gene_symbol='PARP1') "
                    "or targetId from GtoPdb_search_targets for more complete results."
                )

            return result
        except Exception as e:
            return {
                "status": "error",
                "error": f"GtoPdb API error: {str(e)}",
                "url": url,
            }

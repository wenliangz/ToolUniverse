import requests
from typing import Any, Dict
from .base_tool import BaseTool
from .http_utils import request_with_retry
from .tool_registry import register_tool


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

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        url = None
        self._pending_ligand_id_filter = None  # BUG-38B-02: reset per call
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

            # BUG-38B-02: client-side filter by ligandId when requested
            # (/ligands/{id}/interactions always returns [], so we fetch all and filter)
            ligand_id_filter = getattr(self, "_pending_ligand_id_filter", None)
            if ligand_id_filter is not None and isinstance(data, list):
                data = [x for x in data if x.get("ligandId") == ligand_id_filter]

            # Apply limit if specified (max_results is an alias for limit)
            limit = arguments.get("limit", arguments.get("max_results", 20))
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
                    "interactions database. Note: GtoPdb's /interactions endpoint covers "
                    "receptor pharmacology (GPCR, ion channel, enzyme, transporter) data. "
                    "Kinase inhibitors and other mechanism-based drugs may not appear here. "
                    "To find targets, search GtoPdb using the ligand name on guidetopharmacology.org."
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

            return result
        except Exception as e:
            return {
                "status": "error",
                "error": f"GtoPdb API error: {str(e)}",
                "url": url,
            }

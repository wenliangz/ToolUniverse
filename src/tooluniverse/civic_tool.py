"""
CIViC (Clinical Interpretation of Variants in Cancer) API tool for ToolUniverse.

CIViC is a community knowledgebase for expert-curated interpretations of variants
in cancer. It provides clinical evidence levels and interpretations.

API Documentation: https://civicdb.org/api
GraphQL Endpoint: https://civicdb.org/api/graphql
"""

import requests
from typing import Dict, Any, Optional
from .base_tool import BaseTool
from .tool_registry import register_tool

# Base URL for CIViC
CIVIC_BASE_URL = "https://civicdb.org/api"
CIVIC_GRAPHQL_URL = f"{CIVIC_BASE_URL}/graphql"


@register_tool("CIViCTool")
class CIViCTool(BaseTool):
    """
    Tool for querying CIViC (Clinical Interpretation of Variants in Cancer).

    CIViC provides:
    - Expert-curated cancer variant interpretations
    - Clinical evidence levels
    - Drug-variant associations
    - Disease-variant associations

    Uses GraphQL API. No authentication required. Free for academic/research use.
    """

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        fields = tool_config.get("fields", {})
        self.query_template: str = fields.get("query", "")
        self.operation_name: Optional[str] = fields.get("operation_name")
        self.timeout: int = tool_config.get("timeout", 30)
        # array_wrap: maps argument name -> GraphQL variable name, wrapping string in a list
        # e.g. {"gene_symbol": "entrezSymbols"} means arguments["gene_symbol"] -> variables["entrezSymbols"] = [value]
        self.array_wrap: Dict[str, str] = fields.get("array_wrap", {})
        # param_map: maps argument name -> GraphQL variable name (without list wrapping)
        # e.g. {"therapy": "therapyName"} means arguments["therapy"] -> variables["therapyName"] = value
        self.param_map: Dict[str, str] = fields.get("param_map", {})
        # variable_defaults: applies default values for GraphQL variables not supplied by user
        # e.g. {"status": "ACCEPTED"} sets status=ACCEPTED when not explicitly provided
        self.variable_defaults: Dict[str, Any] = fields.get("variable_defaults", {})

    def _build_graphql_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Build GraphQL query from template and arguments."""
        query = self.query_template

        # GraphQL queries use variables, not string replacement
        # Extract variable names from query (e.g., $limit, $gene_id)
        import re

        var_matches = re.findall(r"\$(\w+)", query)

        # Map arguments to GraphQL variables
        # GraphQL variable names match argument names in our config
        variables = {}
        for var_name in var_matches:
            # Check if argument exists (variable name matches argument name)
            if var_name in arguments:
                variables[var_name] = arguments[var_name]

        # Handle array_wrap: convert string arguments to lists for array-typed GraphQL variables
        for arg_name, var_name in self.array_wrap.items():
            if arg_name in arguments and arguments[arg_name] is not None:
                val = arguments[arg_name]
                variables[var_name] = [val] if not isinstance(val, list) else val

        # Handle param_map: rename argument names to GraphQL variable names
        # Only sets the variable if not already set by direct name match
        for arg_name, var_name in self.param_map.items():
            if arg_name in arguments and arguments[arg_name] is not None:
                if var_name not in variables:
                    variables[var_name] = arguments[arg_name]

        # Apply variable_defaults: set defaults for variables not already set by arguments
        for var_name, default_val in self.variable_defaults.items():
            if var_name not in variables and var_name in var_matches:
                variables[var_name] = default_val

        payload = {"query": query}

        if self.operation_name:
            payload["operationName"] = self.operation_name

        if variables:
            payload["variables"] = variables

        return payload

    def _lookup_gene_id(self, gene_name: str) -> Optional[int]:
        """Look up CIViC gene ID by gene symbol via GraphQL."""
        payload = {
            "query": "query GetGenes($entrezSymbols: [String!]) { genes(entrezSymbols: $entrezSymbols) { nodes { id name } } }",
            "variables": {"entrezSymbols": [gene_name.upper()]},
        }
        try:
            resp = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=10,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = resp.json().get("data", {})
            nodes = data.get("genes", {}).get("nodes", [])
            if nodes:
                return nodes[0]["id"]
        except Exception:
            pass
        return None

    def _get_variants_for_gene_id(
        self, gene_id: int, limit: int = 200
    ) -> Dict[str, Any]:
        """Fetch variants for a given CIViC gene_id via GraphQL."""
        payload = {
            # BUG-41A-02: include feature { id name } in variant nodes so callers can
            # distinguish e.g. KRAS G12C (ID 78) from NRAS G12C (ID 897).
            # CIViC uses 'feature' (not 'gene') as the field on GeneVariant type.
            "query": "query GetVariantsByGene($gene_id: Int!, $limit: Int) { gene(id: $gene_id) { id name variants(first: $limit) { nodes { id name ... on GeneVariant { feature { id name } } } } } }",
            "operationName": "GetVariantsByGene",
            "variables": {"gene_id": gene_id, "limit": limit},
        }
        try:
            resp = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=30,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = resp.json().get("data", {})
            return {
                "data": data,
                "metadata": {"source": "CIViC", "format": "GraphQL"},
            }
        except Exception as e:
            return {"error": f"CIViC API request failed: {str(e)}"}

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the CIViC GraphQL API call."""
        tool_name = self.tool_config.get("name", "")

        # civic_get_variants_by_gene: resolve gene_name → gene_id if needed
        if tool_name == "civic_get_variants_by_gene":
            if not arguments.get("gene_id"):
                gene_name = (
                    arguments.get("gene_name")
                    or arguments.get("gene")
                    or arguments.get("query")
                )
                if not gene_name:
                    return {
                        "error": "gene_id or gene_name is required for civic_get_variants_by_gene"
                    }
                gene_id = self._lookup_gene_id(gene_name)
                if gene_id is None:
                    return {"error": f"Gene '{gene_name}' not found in CIViC database"}
                arguments = dict(arguments)
                arguments["gene_id"] = gene_id
            return self._get_variants_for_gene_id(
                arguments["gene_id"], arguments.get("limit", 200)
            )

        # BUG-40B-01: civic_search_evidence_items — warn on unsupported gene/variant params.
        # BUG-41A-03: also catch molecular_profile_id (integer) — no GraphQL binding.
        # These parameters are not in the GraphQL schema and are silently ignored.
        if tool_name == "civic_search_evidence_items":
            unsupported = [
                p
                for p in ("gene", "variant", "gene_name", "molecular_profile_id")
                if arguments.get(p)
            ]
            if unsupported:
                gene = arguments.get("gene") or arguments.get("gene_name")
                variant = arguments.get("variant")
                mol_id = arguments.get("molecular_profile_id")
                profile_hint = ""
                if gene and variant:
                    profile_hint = f' Try: molecular_profile="{gene} {variant}"'
                elif gene:
                    profile_hint = f' Try: molecular_profile="{gene}"'
                elif mol_id:
                    profile_hint = (
                        f" For integer ID filtering, use civic_get_evidence_item with the "
                        f"evidence ID, or civic_get_variant with the variant ID."
                    )
                return {
                    "error": f"Unsupported parameter(s) for civic_search_evidence_items: {', '.join(unsupported)}. "
                    "Supported filters: molecular_profile (string, e.g. 'BRAF V600E'), "
                    "therapy, disease, status." + profile_hint,
                }

        # civic_search_variants: if gene/gene_name provided, look up gene_id then get variants.
        # BUG-41A-01: also handle combined gene+query — get gene variants, filter client-side.
        if tool_name == "civic_search_variants":
            gene_name = arguments.get("gene") or arguments.get("gene_name")
            query_term = arguments.get("query")
            if gene_name:
                gene_id = self._lookup_gene_id(gene_name)
                if gene_id is None:
                    return {"error": f"Gene '{gene_name}' not found in CIViC database"}
                # BUG-43B-01: when gene+query combined, always fetch up to 200 variants
                # before client-side filtering; the user's limit applies to the OUTPUT,
                # not the pre-filter fetch — otherwise alphabetically early variants may
                # block clinically important ones (e.g. FLT3 ITD at position >10).
                user_limit = arguments.get("limit")
                fetch_limit = 200 if query_term else (user_limit or 200)
                result = self._get_variants_for_gene_id(gene_id, fetch_limit)
                # If query also provided, filter returned variants by name client-side
                if query_term and isinstance(result.get("data"), dict):
                    gene_data = result["data"].get("gene", {})
                    nodes = gene_data.get("variants", {}).get("nodes", [])
                    q_lower = query_term.lower()
                    filtered = [
                        v for v in nodes if q_lower in v.get("name", "").lower()
                    ]
                    # Truncate to user-requested limit AFTER filtering
                    if user_limit:
                        filtered = filtered[:user_limit]
                    gene_data.get("variants", {})["nodes"] = filtered
                    # BUG-43A-04: when gene+query filter returns empty, add a helpful note.
                    # CIViC stores fusions as molecular profiles (not gene variants).
                    if not filtered:
                        fusion_hint = ""
                        if "fusion" in q_lower:
                            fusion_hint = (
                                f" CIViC stores fusion events as molecular profiles "
                                f"rather than gene variants. Try civic_search_evidence_items "
                                f"with molecular_profile='{gene_name}::PARTNER Fusion' "
                                f"(e.g., '{gene_name}::BICC1 Fusion')."
                            )
                        result["note"] = (
                            f"No variants found matching '{query_term}' in {gene_name}."
                            + fusion_hint
                        )
                return result

        try:
            # Build GraphQL query
            payload = self._build_graphql_query(arguments)

            # Make GraphQL request
            response = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/CIViC",
                },
            )

            response.raise_for_status()
            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                return {
                    "error": "GraphQL query errors",
                    "errors": data["errors"],
                    "query": arguments,
                }

            return {
                "data": data.get("data", {}),
                "metadata": {
                    "source": "CIViC (Clinical Interpretation of Variants in Cancer)",
                    "format": "GraphQL",
                    "endpoint": CIVIC_GRAPHQL_URL,
                },
            }

        except requests.RequestException as e:
            return {"error": f"CIViC API request failed: {str(e)}", "query": arguments}
        except ValueError as e:
            return {"error": str(e), "query": arguments}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "query": arguments}

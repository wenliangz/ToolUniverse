"""
SYNERGxDB Drug Combination Synergy Database Tool

Provides access to the SYNERGxDB REST API for querying drug combination
synergy screening data across multiple cancer cell line datasets.

SYNERGxDB integrates 22,507 unique drug combinations (1977 compounds)
screened against 151 cancer cell lines from 9 major studies including
NCI-ALMANAC, MERCK, and AstraZeneca.

API base: https://synergxdb.ca/api/
No authentication required.

Reference: Seo et al., NAR 2020 (PMID: 32442307)
"""

import requests
from typing import Dict, Any
from .base_tool import BaseTool
from .tool_registry import register_tool


SYNERGXDB_BASE_URL = "https://synergxdb.ca/api"


@register_tool("SYNERGxDBTool")
class SYNERGxDBTool(BaseTool):
    """
    Tool for querying the SYNERGxDB drug combination synergy database.

    SYNERGxDB is a comprehensive database integrating drug combination
    screening data from 9 major studies with synergy scores (Bliss, Loewe,
    HSA, ZIP) and pharmacogenomic biomarker associations.

    Supported operations:
    - search_combos: Search drug combination synergy scores
    - get_combo_matrix: Get dose-response matrix data
    - list_drugs: List all drugs in the database
    - get_drug: Get drug details by ID
    - list_cell_lines: List all cell lines
    - list_datasets: List all screening datasets
    - get_combo_stats: Get per-dataset combination statistics
    """

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.parameter = tool_config.get("parameter", {})
        self.required = self.parameter.get("required", [])
        self.session = requests.Session()
        self.timeout = 30

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the SYNERGxDB API tool with given arguments."""
        operation = arguments.get("operation")
        if not operation:
            # Infer operation from tool config (each tool has a fixed const operation)
            schema_op = (
                self.tool_config.get("parameter", {})
                .get("properties", {})
                .get("operation", {})
                .get("enum", [None])[0]
            )
            if schema_op:
                operation = schema_op
            else:
                return {
                    "status": "error",
                    "error": "Missing required parameter: operation",
                }

        operation_handlers = {
            "search_combos": self._search_combos,
            "get_combo_matrix": self._get_combo_matrix,
            "list_drugs": self._list_drugs,
            "get_drug": self._get_drug,
            "list_cell_lines": self._list_cell_lines,
            "list_datasets": self._list_datasets,
            "get_combo_stats": self._get_combo_stats,
        }

        handler = operation_handlers.get(operation)
        if not handler:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}",
                "available_operations": list(operation_handlers.keys()),
            }

        try:
            return handler(arguments)
        except requests.exceptions.Timeout:
            return {"status": "error", "error": "SYNERGxDB API request timed out"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "error": "Failed to connect to SYNERGxDB API"}
        except Exception as e:
            return {"status": "error", "error": f"SYNERGxDB operation failed: {str(e)}"}

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request to SYNERGxDB API."""
        url = f"{SYNERGXDB_BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params or {}, timeout=self.timeout)
        if response.status_code == 200:
            return {"ok": True, "data": response.json()}
        elif response.status_code == 404:
            # BUG-36A-04: 404 means no data for these params (a normal research outcome),
            # not a real error. Return ok=True with empty data so callers can handle it
            # as empty results (exit code 0) rather than a failure (exit code 1).
            return {"ok": True, "data": [], "no_data": True}
        elif response.status_code == 400:
            try:
                err = response.json()
                return {
                    "ok": False,
                    "error": err.get("error", err.get("message", "Bad request")),
                }
            except Exception:
                return {"ok": False, "error": "Bad request - check parameters"}
        else:
            return {
                "ok": False,
                "error": f"API request failed with status {response.status_code}",
                "detail": response.text[:500],
            }

    # BUG-37A-05: dataset name → ID mapping (from /api/datasets/)
    _DATASET_NAME_TO_ID = {
        "NCI-ALMANAC": 2,
        "MERCK": 1,
        "MIT-MELANOMA": 7,
        "VISAGE": 10,
        "DECREASE": 9,
        "YALE-TNBC": 5,
        "YALE-PDAC": 4,
        "STANFORD": 8,
        "CLOUD": 6,
    }

    def _search_combos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search drug combination synergy scores."""
        drug_id_1 = arguments.get("drug_id_1")
        drug_id_2 = arguments.get("drug_id_2")
        sample = arguments.get("sample")
        dataset = arguments.get("dataset")
        page = arguments.get("page", 1)
        per_page = arguments.get("per_page", 20)

        # BUG-37A-05: accept dataset as string name and convert to integer ID
        if dataset is not None and isinstance(dataset, str) and not dataset.isdigit():
            mapped = self._DATASET_NAME_TO_ID.get(dataset.upper())
            if mapped is not None:
                dataset = mapped
            else:
                available = ", ".join(self._DATASET_NAME_TO_ID.keys())
                return {
                    "status": "error",
                    "error": f"Unknown dataset name '{dataset}'. Available: {available}. "
                    "You can also pass the integer dataset ID directly.",
                }

        if not drug_id_1 and not drug_id_2 and not dataset:
            return {
                "status": "error",
                "error": "At least one of drug_id_1, drug_id_2, or dataset is required. "
                "To find drug IDs, use SYNERGxDB_list_drugs (filter by name with 'query' param). "
                "To find dataset IDs/names, use SYNERGxDB_list_datasets. "
                "The sample/tissue filter can only be used alongside these parameters.",
            }

        params = {"page": page, "perPage": per_page}
        if drug_id_1:
            params["drugId1"] = drug_id_1
        if drug_id_2:
            params["drugId2"] = drug_id_2
        if sample:
            params["sample"] = sample
        if dataset:
            params["dataset"] = dataset

        result = self._make_request("combos/", params)
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        if result.get("no_data") or not data:
            return {
                "status": "success",
                "data": [],
                "count": 0,
                "message": "No combination data found for the given parameters in SYNERGxDB.",
            }
        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

    def _get_combo_matrix(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get dose-response matrix for a specific drug combination."""
        combo_id = arguments.get("combo_id")
        source_id = arguments.get("source_id")

        if not combo_id or not source_id:
            return {
                "status": "error",
                "error": "Both combo_id and source_id are required",
            }

        result = self._make_request(
            "combos/matrix",
            {
                "comboId": combo_id,
                "idSource": source_id,
            },
        )
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

    def _list_drugs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all drugs in the SYNERGxDB database."""
        result = self._make_request("drugs/")
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]

        # BUG-35A-08: client-side name filtering if query/name/search is provided
        name_filter = (
            arguments.get("query") or arguments.get("name") or arguments.get("search")
        )
        if name_filter and isinstance(data, list):
            name_lower = name_filter.lower()
            data = [
                d
                for d in data
                if name_lower in str(d.get("drug_name", "")).lower()
                or name_lower in str(d.get("name", "")).lower()
            ]

        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

    def _get_drug(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get drug details by ID."""
        drug_id = arguments.get("drug_id")
        if not drug_id:
            return {"status": "error", "error": "drug_id is required"}

        result = self._make_request(f"drugs/{drug_id}")
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        # API returns a list with one element
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        return {
            "status": "success",
            "data": data,
        }

    def _list_cell_lines(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all cell lines in the SYNERGxDB database."""
        result = self._make_request("cell_lines/")
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

    def _list_datasets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List all screening datasets in SYNERGxDB."""
        result = self._make_request("datasets/")
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

    def _get_combo_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get per-dataset combination statistics."""
        result = self._make_request("combos/stats")
        if not result["ok"]:
            return {"status": "error", "error": result["error"]}

        data = result["data"]
        return {
            "status": "success",
            "data": data,
            "count": len(data),
        }

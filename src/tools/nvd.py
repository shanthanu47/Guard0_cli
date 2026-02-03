import httpx
from diskcache import Cache
import logging

# Setup Cache (TTL 24 hours)
cache = Cache('./data/cache')

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class NVDClient:
    def __init__(self, api_key: str = None):
        self.headers = {"User-Agent": "VulnBot-CLI/1.0"}
        if api_key:
            self.headers["apiKey"] = api_key

    def get_cve(self, cve_id: str):
        """
        Fetches CVE details from NVD API with local caching.
        """
        cve_id = cve_id.upper().strip()
        
        # 1. Check Cache
        cached_data = cache.get(cve_id)
        if cached_data:
            logging.info(f"Cache Hit for {cve_id}")
            return cached_data

        # 2. API Call
        try:
            params = {"cveId": cve_id}
            with httpx.Client() as client:
                response = client.get(
                    NVD_BASE_URL, 
                    headers=self.headers, 
                    params=params, 
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                # NVD returns a list of "vulnerabilities". We want the first one.
                if data.get("vulnerabilities"):
                    vuln_data = data["vulnerabilities"][0]["cve"]
                    
                    # 3. Save to Cache
                    cache.set(cve_id, vuln_data, expire=86400) # 24 hrs
                    return vuln_data
                else:
                    return {"error": "CVE not found"}

        except Exception as e:
            return {"error": f"API Error: {str(e)}"}

# Singleton instance to be used by the tool
nvd_client = NVDClient()

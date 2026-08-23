import asyncio
import time
import uuid
from typing import Any, Dict, List, Optional
from collections import deque

from server.services.scraper_service import scraper_service


class CrawlerService:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def get_active_count(self) -> int:
        return sum(1 for j in self.jobs.values() if j.get("status") in ("pending", "scraping", "running"))

    def get_active_crawls(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": j["id"],
                "status": j["status"],
                "total": j.get("total", 0),
                "completed": j.get("completed", 0),
                "creditsUsed": j.get("completed", 0),
                "expiresAt": j.get("expiresAt", ""),
            }
            for j in self.jobs.values()
            if j.get("status") in ("pending", "scraping", "running")
        ]

    async def _run_crawl(
        self,
        job_id: str,
        seed_url: str,
        max_depth: int = 1,
        max_pages: int = 10,
        formats: Optional[List[str]] = None,
    ):
        formats = formats or ["markdown"]
        job = self.jobs[job_id]
        job["status"] = "scraping"

        visited = set()
        queue = deque([(seed_url, 0)])
        results = []

        try:
            while queue and len(results) < max_pages and job["status"] == "scraping":
                current_url, depth = queue.popleft()
                if current_url in visited:
                    continue
                visited.add(current_url)

                try:
                    res = await scraper_service.scrape(current_url, formats=formats)
                    if res.get("success"):
                        results.append(res["data"])
                        job["completed"] = len(results)
                        job["data"] = results

                    if depth < max_depth and len(results) + len(queue) < max_pages:
                        links = await scraper_service.map_links(current_url, limit=max_pages)
                        for link in links:
                            if link not in visited and link not in [q[0] for q in queue]:
                                queue.append((link, depth + 1))
                except Exception:
                    pass

                await asyncio.sleep(0.1)

            job["status"] = "completed" if job["status"] != "cancelled" else "cancelled"
            job["total"] = len(results)
            job["completed"] = len(results)
            job["data"] = results
        except asyncio.CancelledError:
            job["status"] = "cancelled"
        except Exception as e:
            job["status"] = "failed"
            job["error"] = str(e)

    def start_crawl(
        self,
        url: str,
        max_depth: int = 1,
        max_pages: int = 10,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "jobId": job_id,
            "success": True,
            "status": "pending",
            "url": f"/v1/crawl/{job_id}",
            "total": max_pages,
            "completed": 0,
            "creditsUsed": 0,
            "expiresAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 86400)),
            "data": [],
        }
        self.jobs[job_id] = job

        task = asyncio.create_task(
            self._run_crawl(job_id, url, max_depth=max_depth, max_pages=max_pages, formats=formats)
        )
        self.running_tasks[job_id] = task
        return job

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        return {
            "success": True,
            "status": job["status"],
            "total": job.get("total", len(job.get("data", []))),
            "completed": job.get("completed", len(job.get("data", []))),
            "creditsUsed": job.get("completed", len(job.get("data", []))),
            "expiresAt": job.get("expiresAt", ""),
            "data": job.get("data", []),
        }

    def cancel_crawl(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if not job:
            return False
        job["status"] = "cancelled"
        task = self.running_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
        return True


crawler_service = CrawlerService()

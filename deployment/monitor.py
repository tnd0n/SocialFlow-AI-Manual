#!/usr/bin/env python3
"""
SocialFlow AI - Monitoring and Health Check Script
Monitors account health, execution success rates, and platform restrictions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor system health and account status"""

    def __init__(self):
        self.health_report = {
            "check_time": datetime.now().isoformat(),
            "overall_status": "unknown",
            "platform_health": {},
            "recent_performance": {},
            "recommendations": []
        }

    async def check_account_health(self) -> Dict[str, Any]:
        """Check if accounts are healthy and not restricted"""
        platforms = ["reddit", "telegram", "threads", "instagram"]
        health_status = {}

        for platform in platforms:
            try:
                # Check for recent successful actions
                recent_success = await self.check_recent_success(platform)

                # Check for error patterns
                error_rate = await self.check_error_rate(platform)

                # Check rate limit status
                rate_limit_status = await self.check_rate_limits(platform)

                health_status[platform] = {
                    "status": "healthy" if recent_success and error_rate < 0.3 else "warning",
                    "recent_success_rate": recent_success,
                    "error_rate": error_rate,
                    "rate_limited": rate_limit_status,
                    "last_successful_action": await self.get_last_success_time(platform)
                }

            except Exception as e:
                health_status[platform] = {
                    "status": "error",
                    "error": str(e)
                }

        return health_status

    async def check_recent_success(self, platform: str) -> float:
        """Check recent success rate for a platform"""
        # Parse execution logs for success rate
        log_file = Path("EXECUTION_LOG.md")
        if not log_file.exists():
            return 0.0

        # Simple parsing - in production would use structured logs
        content = log_file.read_text()

        # Count successes vs failures for this platform
        # This is a simplified implementation
        success_count = content.count(f"{platform.title()}: success")
        total_count = content.count(f"{platform.title()}:")

        if total_count == 0:
            return 0.0

        return success_count / total_count

    async def check_error_rate(self, platform: str) -> float:
        """Check error rate for a platform"""
        # Similar to success rate but for errors
        log_file = Path("daily_execution.log")
        if not log_file.exists():
            return 0.0

        try:
            content = log_file.read_text()
            error_count = content.count(f"{platform} failed") + content.count(f"{platform} error")
            total_count = content.count(platform)

            if total_count == 0:
                return 0.0

            return error_count / total_count

        except Exception:
            return 1.0  # Assume high error rate if can't read logs

    async def check_rate_limits(self, platform: str) -> bool:
        """Check if platform is currently rate limited"""
        # Check recent logs for rate limit indicators
        log_file = Path("daily_execution.log")
        if not log_file.exists():
            return False

        try:
            content = log_file.read_text()
            rate_limit_indicators = [
                "rate limit", "too many requests", "429", "rate_limited"
            ]

            for indicator in rate_limit_indicators:
                if indicator in content.lower() and platform in content.lower():
                    return True

            return False

        except Exception:
            return True  # Assume rate limited if can't check

    async def get_last_success_time(self, platform: str) -> str:
        """Get timestamp of last successful action for platform"""
        # This would parse logs to find last success
        # Simplified implementation
        return "unknown"

    async def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        trends = {
            "daily_success_rates": [],
            "popular_content_types": {},
            "optimal_posting_times": {},
            "engagement_patterns": {}
        }

        # Parse historical logs to identify trends
        # This is a placeholder for more sophisticated analysis

        return trends

    async def generate_recommendations(self, health_data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on health data"""
        recommendations = []

        for platform, health in health_data.items():
            if health.get("status") == "warning":
                if health.get("error_rate", 0) > 0.5:
                    recommendations.append(f"High error rate on {platform} - check authentication and content quality")

                if health.get("rate_limited"):
                    recommendations.append(f"{platform} is rate limited - reduce posting frequency")

                if health.get("recent_success_rate", 0) < 0.3:
                    recommendations.append(f"Low success rate on {platform} - review content strategy")

            elif health.get("status") == "error":
                recommendations.append(f"{platform} has critical errors - check logs and credentials")

        # General recommendations
        if len([h for h in health_data.values() if h.get("status") == "healthy"]) < 2:
            recommendations.append("Multiple platforms having issues - consider reducing overall activity")

        return recommendations

    async def save_health_report(self, report: Dict[str, Any]):
        """Save health report to file"""
        report_file = Path("logs/health_report.json")
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Health report saved to {report_file}")

    async def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        logger.info("🩺 Running SocialFlow AI health check...")

        # Check account health
        platform_health = await self.check_account_health()

        # Analyze performance trends
        performance_trends = await self.analyze_performance_trends()

        # Generate recommendations
        recommendations = await self.generate_recommendations(platform_health)

        # Determine overall status
        healthy_platforms = len([h for h in platform_health.values() if h.get("status") == "healthy"])
        total_platforms = len(platform_health)

        if healthy_platforms == total_platforms:
            overall_status = "healthy"
        elif healthy_platforms >= total_platforms // 2:
            overall_status = "warning"
        else:
            overall_status = "critical"

        # Compile report
        report = {
            "check_time": datetime.now().isoformat(),
            "overall_status": overall_status,
            "platform_health": platform_health,
            "performance_trends": performance_trends,
            "recommendations": recommendations,
            "healthy_platforms": healthy_platforms,
            "total_platforms": total_platforms
        }

        # Save report
        await self.save_health_report(report)

        # Log summary
        logger.info(f"Health check complete: {overall_status} ({healthy_platforms}/{total_platforms} platforms healthy)")

        if recommendations:
            logger.info("Recommendations:")
            for rec in recommendations:
                logger.info(f"  - {rec}")

        return report

async def main():
    """Main monitoring function"""
    monitor = HealthMonitor()
    report = await monitor.run_health_check()

    # Exit with appropriate code
    if report["overall_status"] == "healthy":
        return 0
    elif report["overall_status"] == "warning":
        return 1
    else:
        return 2

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

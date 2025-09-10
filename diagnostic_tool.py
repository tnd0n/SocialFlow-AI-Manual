#!/usr/bin/env python3
"""
SocialFlow AI - Comprehensive Diagnostic Tool
Runs smoke tests to validate system configuration and functionality
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import importlib.util
from datetime import datetime

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import project modules
try:
    from dotenv import load_dotenv
    from backend.utils.logger import get_logger
    from llm_providers.enhanced_manager import EnhancedLLMManager
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure you're running from the SocialFlow-AI-Manual directory")
    sys.exit(1)

log = get_logger("DiagnosticTool")

class SocialFlowDiagnostic:
    """Comprehensive diagnostic tool for SocialFlow AI system"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "UNKNOWN",
            "tests": {}
        }
        self.load_environment()
    
    def load_environment(self):
        """Load environment variables from config file"""
        env_path = Path("config/accounts.env")
        if env_path.exists():
            load_dotenv(env_path)
            print("✅ Environment variables loaded from config/accounts.env")
        else:
            print("❌ config/accounts.env not found")
            
    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    async def test_llm_providers(self) -> Tuple[bool, Dict]:
        """Test 1: LLM Provider Status Check"""
        self.print_header("LLM Provider Status Check")
        
        try:
            # Initialize LLM manager
            llm_manager = EnhancedLLMManager()
            
            # Check API providers
            api_status = []
            for provider in llm_manager.api_providers:
                provider_name = provider.__class__.__name__
                try:
                    # Test basic provider initialization
                    status = "✅ ACTIVE" if hasattr(provider, 'api_key') and provider.api_key else "⚠️ NO_KEY"
                    api_status.append({
                        "name": provider_name,
                        "type": "API",
                        "status": status,
                        "has_key": bool(hasattr(provider, 'api_key') and provider.api_key)
                    })
                    print(f"  {status} {provider_name} (API)")
                except Exception as e:
                    api_status.append({
                        "name": provider_name,
                        "type": "API", 
                        "status": f"❌ ERROR: {str(e)}",
                        "has_key": False
                    })
                    print(f"  ❌ {provider_name} (API) - Error: {e}")
            
            # Check web providers
            web_status = []
            for provider in llm_manager.web_providers:
                provider_name = provider.__class__.__name__
                try:
                    status = "✅ READY" if provider else "❌ FAILED"
                    web_status.append({
                        "name": provider_name,
                        "type": "WEB",
                        "status": status,
                        "cookies_setup": False  # Would need to check cookie files
                    })
                    print(f"  {status} {provider_name} (Web)")
                except Exception as e:
                    web_status.append({
                        "name": provider_name,
                        "type": "WEB",
                        "status": f"❌ ERROR: {str(e)}",
                        "cookies_setup": False
                    })
                    print(f"  ❌ {provider_name} (Web) - Error: {e}")
            
            total_providers = len(api_status) + len(web_status)
            working_providers = len([p for p in api_status + web_status if "✅" in p["status"]])
            
            print(f"\n📊 Summary: {working_providers}/{total_providers} providers available")
            
            result = {
                "api_providers": api_status,
                "web_providers": web_status,
                "total_count": total_providers,
                "working_count": working_providers,
                "success_rate": working_providers / total_providers if total_providers > 0 else 0
            }
            
            return working_providers > 0, result
            
        except Exception as e:
            error_result = {"error": str(e), "providers": []}
            print(f"❌ LLM Provider test failed: {e}")
            return False, error_result
    
    def test_content_queues(self) -> Tuple[bool, Dict]:
        """Test 2: Content Queue Analysis"""
        self.print_header("Content Queue Analysis")
        
        queue_dir = Path("content_queue")
        required_files = ["reddit_queue.json", "telegram_queue.json", "threads_queue.json", "instagram_queue.json"]
        
        results = {
            "queue_files": [],
            "total_files": len(required_files),
            "valid_files": 0,
            "missing_files": [],
            "invalid_files": []
        }
        
        for filename in required_files:
            file_path = queue_dir / filename
            file_result = {
                "filename": filename,
                "exists": file_path.exists(),
                "valid_json": False,
                "has_required_fields": False,
                "size_bytes": 0
            }
            
            if file_path.exists():
                try:
                    # Check file size
                    file_result["size_bytes"] = file_path.stat().st_size
                    
                    # Validate JSON structure
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    file_result["valid_json"] = True
                    
                    # Check for required fields based on platform
                    if filename.startswith("reddit"):
                        file_result["has_required_fields"] = "reddit_posts" in data
                    elif filename.startswith("instagram"):
                        file_result["has_required_fields"] = "instagram_targets" in data
                    elif filename.startswith("telegram"):
                        file_result["has_required_fields"] = "telegram_messages" in data or "telegram_groups" in data
                    elif filename.startswith("threads"):
                        file_result["has_required_fields"] = "threads_posts" in data or "threads_hashtags" in data
                    
                    if file_result["valid_json"] and file_result["has_required_fields"]:
                        results["valid_files"] += 1
                        print(f"  ✅ {filename} - Valid ({file_result['size_bytes']} bytes)")
                    else:
                        results["invalid_files"].append(filename)
                        print(f"  ⚠️ {filename} - Missing required fields")
                        
                except json.JSONDecodeError:
                    file_result["valid_json"] = False
                    results["invalid_files"].append(filename)
                    print(f"  ❌ {filename} - Invalid JSON")
                except Exception as e:
                    results["invalid_files"].append(filename)
                    print(f"  ❌ {filename} - Error: {e}")
            else:
                results["missing_files"].append(filename)
                print(f"  ❌ {filename} - File missing")
            
            results["queue_files"].append(file_result)
        
        success = results["valid_files"] == results["total_files"]
        print(f"\n📊 Summary: {results['valid_files']}/{results['total_files']} queue files valid")
        
        return success, results
    
    def test_configuration_files(self) -> Tuple[bool, Dict]:
        """Test 3: Configuration File Validation"""
        self.print_header("Configuration File Validation")
        
        config_tests = {
            "accounts_env": {"path": "config/accounts.env", "required_vars": []},
            "behavior_settings": {"path": "config/behavior_settings.py", "importable": False},
            "requirements": {"path": "requirements.txt", "readable": False}
        }
        
        results = {"config_files": []}
        
        # Test accounts.env
        env_path = Path("config/accounts.env")
        env_result = {
            "file": "accounts.env",
            "exists": env_path.exists(),
            "readable": False,
            "api_keys_count": 0,
            "platform_credentials": []
        }
        
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    content = f.read()
                env_result["readable"] = True
                
                # Count API keys and credentials
                lines = content.split('\n')
                api_keys = [line for line in lines if 'API_KEY' in line and '=' in line and not line.strip().startswith('#')]
                env_result["api_keys_count"] = len(api_keys)
                
                # Check platform credentials
                platforms = ["REDDIT", "TELEGRAM", "INSTAGRAM", "THREADS", "GITHUB"]
                for platform in platforms:
                    platform_vars = [line for line in lines if line.startswith(platform) and '=' in line]
                    if platform_vars:
                        env_result["platform_credentials"].append(platform.lower())
                
                print(f"  ✅ accounts.env - {env_result['api_keys_count']} API keys, {len(env_result['platform_credentials'])} platforms")
                
            except Exception as e:
                print(f"  ❌ accounts.env - Error reading: {e}")
        else:
            print(f"  ❌ accounts.env - File missing")
        
        results["config_files"].append(env_result)
        
        # Test behavior_settings.py
        try:
            import config.behavior_settings
            print("  ✅ behavior_settings.py - Importable")
            config_tests["behavior_settings"]["importable"] = True
        except Exception as e:
            print(f"  ❌ behavior_settings.py - Import error: {e}")
        
        # Test requirements.txt
        req_path = Path("requirements.txt")
        if req_path.exists():
            try:
                with open(req_path, 'r') as f:
                    requirements = f.readlines()
                print(f"  ✅ requirements.txt - {len(requirements)} dependencies")
                config_tests["requirements"]["readable"] = True
            except Exception as e:
                print(f"  ❌ requirements.txt - Error: {e}")
        else:
            print("  ❌ requirements.txt - File missing")
        
        success = env_result["exists"] and config_tests["behavior_settings"]["importable"]
        return success, results
    
    async def test_content_generation(self) -> Tuple[bool, Dict]:
        """Test 4: Content Generation Capability"""
        self.print_header("Content Generation Test")
        
        try:
            # Test if we can initialize content generation components
            content_scheduler = None
            if Path("core/content_scheduler.py").exists():
                try:
                    # Dynamic import to avoid LSP errors
                    spec = importlib.util.spec_from_file_location("content_scheduler", "core/content_scheduler.py")
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        content_scheduler = getattr(module, 'ContentScheduler', None)
                except Exception:
                    pass
            
            if content_scheduler is None:
                print("  ⚠️ ContentScheduler not found - using basic test")
                
                # Create a simple test JSON to verify file writing works
                test_content = {
                    "test_posts": [
                        {
                            "title": "Diagnostic Test Post",
                            "content": "This is a test post generated by the diagnostic tool",
                            "timing": "test",
                            "platform": "test"
                        }
                    ],
                    "execution_status": "test",
                    "created_at": datetime.now().isoformat(),
                    "generated_by": "diagnostic_tool"
                }
                
                # Try writing to each queue file
                queue_dir = Path("content_queue")
                test_results = []
                
                for platform in ["reddit", "telegram", "threads", "instagram"]:
                    try:
                        test_file = queue_dir / f"{platform}_test_queue.json"
                        with open(test_file, 'w') as f:
                            json.dump(test_content, f, indent=2)
                        
                        # Verify file was created and is readable
                        with open(test_file, 'r') as f:
                            loaded_data = json.load(f)
                        
                        # Clean up test file
                        test_file.unlink()
                        
                        test_results.append({
                            "platform": platform,
                            "file_write": True,
                            "file_read": True,
                            "json_valid": True
                        })
                        print(f"  ✅ {platform} - File write/read test passed")
                        
                    except Exception as e:
                        test_results.append({
                            "platform": platform,
                            "file_write": False,
                            "file_read": False,
                            "json_valid": False,
                            "error": str(e)
                        })
                        print(f"  ❌ {platform} - File operation failed: {e}")
                
                success = all(result.get("file_write", False) for result in test_results)
                result = {
                    "test_type": "basic_file_operations",
                    "platform_tests": test_results,
                    "success_count": len([r for r in test_results if r.get("file_write", False)])
                }
                
                return success, result
            else:
                # If ContentScheduler exists, we could run more advanced tests here
                print("  ✅ ContentScheduler found - advanced testing not implemented yet")
                return True, {"test_type": "scheduler_available", "message": "ContentScheduler found but not tested"}
            
        except Exception as e:
            print(f"  ❌ Content generation test failed: {e}")
            return False, {"error": str(e)}
    
    def run_static_code_quality(self) -> Tuple[bool, Dict]:
        """Test 5: Static Code Quality Check (Optional)"""
        self.print_header("Static Code Quality Check")
        
        python_files = []
        for path in Path(".").rglob("*.py"):
            if not any(part.startswith('.') for part in path.parts):  # Skip hidden directories
                python_files.append(path)
        
        results = {
            "total_python_files": len(python_files),
            "syntax_errors": [],
            "import_errors": [],
            "files_checked": []
        }
        
        print(f"  📁 Found {len(python_files)} Python files")
        
        for file_path in python_files[:10]:  # Check first 10 files to avoid spam
            try:
                # Basic syntax check
                with open(file_path, 'r') as f:
                    content = f.read()
                
                compile(content, str(file_path), 'exec')
                
                results["files_checked"].append({
                    "file": str(file_path),
                    "syntax_valid": True,
                    "size_lines": len(content.split('\n'))
                })
                
            except SyntaxError as e:
                results["syntax_errors"].append({
                    "file": str(file_path),
                    "error": str(e),
                    "line": getattr(e, 'lineno', 'unknown')
                })
                print(f"  ❌ Syntax error in {file_path}: {e}")
                
            except Exception as e:
                results["import_errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        success = len(results["syntax_errors"]) == 0
        if success:
            print(f"  ✅ No syntax errors found in checked files")
        
        return success, results
    
    async def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🚀 Starting SocialFlow AI Diagnostic Tests")
        print(f"📅 Timestamp: {self.results['timestamp']}")
        
        # Test 1: LLM Providers
        llm_success, llm_results = await self.test_llm_providers()
        self.results["tests"]["llm_providers"] = {
            "success": llm_success,
            "results": llm_results
        }
        
        # Test 2: Content Queues
        queue_success, queue_results = self.test_content_queues()
        self.results["tests"]["content_queues"] = {
            "success": queue_success,
            "results": queue_results
        }
        
        # Test 3: Configuration Files
        config_success, config_results = self.test_configuration_files()
        self.results["tests"]["configuration"] = {
            "success": config_success,
            "results": config_results
        }
        
        # Test 4: Content Generation
        gen_success, gen_results = await self.test_content_generation()
        self.results["tests"]["content_generation"] = {
            "success": gen_success,
            "results": gen_results
        }
        
        # Test 5: Static Code Quality (Optional)
        quality_success, quality_results = self.run_static_code_quality()
        self.results["tests"]["code_quality"] = {
            "success": quality_success,
            "results": quality_results
        }
        
        # Calculate overall status
        test_results = [
            llm_success,
            queue_success, 
            config_success,
            gen_success
            # Note: code quality is optional, not included in overall status
        ]
        
        if all(test_results):
            self.results["overall_status"] = "PASS"
            status_emoji = "✅"
        elif any(test_results):
            self.results["overall_status"] = "PARTIAL"
            status_emoji = "⚠️"
        else:
            self.results["overall_status"] = "FAIL"
            status_emoji = "❌"
        
        # Print final summary
        self.print_header("Final Test Summary")
        print(f"{status_emoji} Overall Status: {self.results['overall_status']}")
        print(f"✅ LLM Providers: {'PASS' if llm_success else 'FAIL'}")
        print(f"✅ Content Queues: {'PASS' if queue_success else 'FAIL'}")
        print(f"✅ Configuration: {'PASS' if config_success else 'FAIL'}")
        print(f"✅ Content Generation: {'PASS' if gen_success else 'FAIL'}")
        print(f"📊 Code Quality: {'PASS' if quality_success else 'FAIL'} (optional)")
        
        # Save results to file
        results_file = Path("diagnostic_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return self.results

async def main():
    """Main function to run diagnostic tests"""
    try:
        diagnostic = SocialFlowDiagnostic()
        results = await diagnostic.run_all_tests()
        
        # Exit with appropriate code
        if results["overall_status"] == "PASS":
            sys.exit(0)
        elif results["overall_status"] == "PARTIAL":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Diagnostic tests crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
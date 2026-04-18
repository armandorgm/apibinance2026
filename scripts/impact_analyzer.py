import os
import ast
import re
import json
import argparse
from pathlib import Path

class DependencyAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir).resolve()
        self.graph = {}  # file -> [dependencies]
        self.reverse_graph = {}  # file -> [dependents]
        self.temp_dir = self.root_dir / ".temp"
        self.deps_file = self.temp_dir / "deps.json"

    def normalize_path(self, path):
        try:
            return str(Path(path).relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def parse_python_imports(self, file_path):
        imports = set()
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ""
                level = node.level
                if level > 0:
                    # Handle relative imports (rudimentary resolve)
                    parent = Path(file_path).parents[level-1]
                    try:
                        rel_module = str(parent.relative_to(self.root_dir / "backend")).replace("\\", ".").replace("/", ".")
                        full_module = f"{rel_module}.{module}" if module else rel_module
                        imports.add(full_module)
                    except ValueError:
                        pass
                else:
                    imports.add(module)
        
        # Convert modules to file paths if possible
        resolved_files = set()
        for imp in imports:
            # Look for app.something -> backend/app/something.py
            parts = imp.split(".")
            if parts[0] == "app":
                potential_file = self.root_dir / "backend" / ("/".join(parts) + ".py")
                if potential_file.exists():
                    resolved_files.add(self.normalize_path(potential_file))
                else:
                    potential_dir = self.root_dir / "backend" / ("/".join(parts) / "__init__.py")
                    if potential_dir.exists():
                        resolved_files.add(self.normalize_path(potential_dir))
        
        return resolved_files

    def parse_typescript_imports(self, file_path):
        imports = set()
        # Simple regex for imports: import ... from './path' or '@/path'
        regex = r"from\s+['\"](@\/|(?:\.\.?\/).*?)['\"]"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(regex, content)
            for match in matches:
                resolved_path = None
                if match.startswith("@/"):
                    # Alias @/ -> frontend/
                    sub_path = match[2:]
                    potential_files = [
                        self.root_dir / "frontend" / f"{sub_path}.ts",
                        self.root_dir / "frontend" / f"{sub_path}.tsx",
                        self.root_dir / "frontend" / f"{sub_path}/index.ts",
                        self.root_dir / "frontend" / f"{sub_path}/index.tsx",
                    ]
                    for p in potential_files:
                        if p.exists():
                            resolved_path = p
                            break
                elif match.startswith("."):
                    # Relative path
                    parent = Path(file_path).parent
                    potential_files = [
                        (parent / match).resolve(),
                        (parent / f"{match}.ts").resolve(),
                        (parent / f"{match}.tsx").resolve(),
                        (parent / f"{match}/index.ts").resolve(),
                        (parent / f"{match}/index.tsx").resolve(),
                    ]
                    for p in potential_files:
                        if p.exists():
                            resolved_path = p
                            break
                
                if resolved_path:
                    imports.add(self.normalize_path(resolved_path))
        
        return imports

    def scan(self):
        print(f"[SCAN] Scanning project in {self.root_dir}...")
        self.graph = {}
        for ext in ["py", "ts", "tsx"]:
            for path in self.root_dir.rglob(f"*.{ext}"):
                if "node_modules" in str(path) or ".next" in str(path) or ".venv" in str(path):
                    continue
                
                norm_path = self.normalize_path(path)
                if ext == "py":
                    deps = self.parse_python_imports(path)
                else:
                    deps = self.parse_typescript_imports(path)
                
                self.graph[norm_path] = list(deps)

        # Build reverse graph
        self.reverse_graph = {}
        for node, edges in self.graph.items():
            for edge in edges:
                if edge not in self.reverse_graph:
                    self.reverse_graph[edge] = []
                self.reverse_graph[edge].append(node)

        # Save to temp
        if not self.temp_dir.exists():
            self.temp_dir.mkdir()
        
        with open(self.deps_file, "w") as f:
            json.dump({"graph": self.graph, "reverse_graph": self.reverse_graph}, f, indent=4)
        
        print(f"[SUCCESS] Scan complete. Data saved to {self.deps_file}")

    def load(self):
        if not self.deps_file.exists():
            self.scan()
        else:
            with open(self.deps_file, "r") as f:
                data = json.load(f)
                self.graph = data["graph"]
                self.reverse_graph = data["reverse_graph"]

    def get_impact(self, target_file):
        norm_target = self.normalize_path(Path(target_file).resolve())
        print(f"[IMPACT] Calculating impact for: {norm_target}")
        
        impacted = set()
        queue = [norm_target]
        visited = {norm_target}

        while queue:
            current = queue.pop(0)
            if current in self.reverse_graph:
                for dependent in self.reverse_graph[current]:
                    if dependent not in visited:
                        impacted.add(dependent)
                        visited.add(dependent)
                        queue.append(dependent)
        
        return sorted(list(impacted))

    def analyze_api_impact(self):
        # Specific logic to link backend routes to frontend fetchers
        routes_file = "backend/app/api/routes.py"
        api_client = "frontend/lib/api.ts"
        
        print(f"[LINK] Analyzing API-to-Frontend mapping...")
        if not os.path.exists(self.root_dir / routes_file): return

        with open(self.root_dir / routes_file, "r") as f:
            content = f.read()
            # Find routes like @router.get("/path")
            routes = re.findall(r'@router\.(?:get|post|put|delete)\("([^"]+)"', content)
        
        mapping = {}
        for route in routes:
            # Search for this route string in frontend
            # We use a simple grep-like search in the API client first
            with open(self.root_dir / api_client, "r") as f:
                client_content = f.read()
                if route in client_content:
                    mapping[route] = [api_client]
        
        return mapping

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DIAS - Dependency & Impact Analysis System")
    parser.add_argument("--scan", action="store_true", help="Perform a full project scan")
    parser.add_argument("--impact", type=str, help="Calculate the impact of changing a specific file")
    parser.add_argument("--api", action="store_true", help="Analyze API-to-Frontend impact")
    
    args = parser.parse_args()
    analyzer = DependencyAnalyzer(os.getcwd())

    if args.scan:
        analyzer.scan()
    elif args.impact:
        analyzer.load()
        impact = analyzer.get_impact(args.impact)
        print(f"Impacted files ({len(impact)}):")
        for f in impact:
            print(f"  - {f}")
    elif args.api:
        mapping = analyzer.analyze_api_impact()
        for route, files in mapping.items():
            print(f"Route: {route} -> {files}")
    else:
        parser.print_help()

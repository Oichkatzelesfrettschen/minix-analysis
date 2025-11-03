#!/usr/bin/env python3
"""
Symbol Extractor - Wrapper for ctags/global
Extracts function definitions, calls, and cross-references from C/assembly
"""

import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Symbol:
    """Represents a code symbol (function, variable, label)"""
    name: str
    kind: str  # function, variable, label, macro
    file: str
    line: int
    signature: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class CallRelationship:
    """Represents a function call relationship"""
    caller: str
    callee: str
    caller_file: str
    caller_line: int

    def to_dict(self):
        return asdict(self)


class SymbolExtractor:
    """Extract symbols using universal-ctags and GNU global"""

    def __init__(self, source_root: Path):
        self.source_root = Path(source_root)
        self.symbols: Dict[str, Symbol] = {}
        self.calls: List[CallRelationship] = []

    def extract_symbols_ctags(self, file_path: Path) -> List[Symbol]:
        """Extract symbols from a file using ctags"""
        symbols = []

        cmd = [
            "ctags",
            "-x",  # Tab-separated output
            "--c-kinds=+fp",  # Functions and prototypes
            "--asm-kinds=+l",  # Include labels in assembly
            "--fields=+n",  # Include line numbers
            str(file_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                # Parse ctags -x output: name kind line file pattern
                parts = line.split(maxsplit=3)
                if len(parts) >= 4:
                    name, kind, line_num, file_info = parts[0], parts[1], parts[2], parts[3]

                    # Extract file path and signature
                    match = re.match(r'([^\s]+)\s+(.*)', file_info)
                    if match:
                        file, signature = match.groups()
                    else:
                        file, signature = file_info, ""

                    symbols.append(Symbol(
                        name=name,
                        kind=kind,
                        file=file,
                        line=int(line_num),
                        signature=signature.strip()
                    ))

        except subprocess.CalledProcessError as e:
            print(f"ctags error: {e}")

        return symbols

    def extract_calls_regex(self, file_path: Path) -> List[CallRelationship]:
        """Extract function calls using regex (fallback/supplement)"""
        calls = []

        if not file_path.exists():
            return calls

        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            return calls

        # Regex patterns for calls
        # C function calls: name(
        c_call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('

        # Assembly calls: call name / jmp name
        asm_call_pattern = r'\b(call|jmp|je|jne|jz|jnz|ja|jb)\s+([a-zA-Z_][a-zA-Z0-9_]*)'

        current_function = None

        for line_num, line in enumerate(content.split('\n'), 1):
            # Detect function definitions (simplified)
            func_def = re.match(r'^\s*(?:static\s+)?(?:inline\s+)?(?:\w+\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            if func_def:
                current_function = func_def.group(1)

            # Detect assembly labels (potential functions)
            asm_label = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):', line)
            if asm_label:
                current_function = asm_label.group(1)

            if not current_function:
                continue

            # Extract C calls
            for match in re.finditer(c_call_pattern, line):
                callee = match.group(1)
                # Filter out keywords and common non-functions
                if callee not in {'if', 'while', 'for', 'switch', 'return', 'sizeof'}:
                    calls.append(CallRelationship(
                        caller=current_function,
                        callee=callee,
                        caller_file=str(file_path.relative_to(self.source_root)),
                        caller_line=line_num
                    ))

            # Extract assembly calls
            for match in re.finditer(asm_call_pattern, line):
                instruction, target = match.groups()
                if target and not target.startswith('.'):  # Skip local labels
                    calls.append(CallRelationship(
                        caller=current_function,
                        callee=target,
                        caller_file=str(file_path.relative_to(self.source_root)),
                        caller_line=line_num
                    ))

        return calls

    def extract_directory(self, directory: Path = None) -> Tuple[List[Symbol], List[CallRelationship]]:
        """Extract symbols and calls from all files in a directory"""
        if directory is None:
            directory = self.source_root

        all_symbols = []
        all_calls = []

        # Find C and assembly files
        for ext in ['*.c', '*.h', '*.S', '*.asm']:
            for file_path in directory.rglob(ext):
                print(f"Processing {file_path.relative_to(self.source_root)}...")

                # Extract symbols
                symbols = self.extract_symbols_ctags(file_path)
                all_symbols.extend(symbols)

                # Extract calls
                calls = self.extract_calls_regex(file_path)
                all_calls.extend(calls)

        self.symbols = {s.name: s for s in all_symbols}
        self.calls = all_calls

        return all_symbols, all_calls

    def to_json(self) -> str:
        """Export symbols and calls as JSON"""
        data = {
            "symbols": [s.to_dict() for s in self.symbols.values()],
            "calls": [c.to_dict() for c in self.calls]
        }
        return json.dumps(data, indent=2)

    def save_json(self, output_path: Path):
        """Save extracted data to JSON file"""
        output_path.write_text(self.to_json())
        print(f"Saved to {output_path}")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Extract symbols and calls from MINIX code")
    parser.add_argument("source_root", type=Path, help="MINIX source root directory")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON file", default=Path("symbols.json"))
    parser.add_argument("-d", "--directory", type=Path, help="Specific directory to analyze (relative to root)")

    args = parser.parse_args()

    extractor = SymbolExtractor(args.source_root)

    target_dir = args.source_root / args.directory if args.directory else args.source_root

    print(f"Extracting symbols from {target_dir}...")
    symbols, calls = extractor.extract_directory(target_dir)

    print(f"Found {len(symbols)} symbols and {len(calls)} call relationships")

    extractor.save_json(args.output)

    print("\nTop 10 most-called functions:")
    call_counts = {}
    for call in calls:
        call_counts[call.callee] = call_counts.get(call.callee, 0) + 1

    for name, count in sorted(call_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {name}: {count} calls")


if __name__ == "__main__":
    main()

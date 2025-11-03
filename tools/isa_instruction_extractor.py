#!/usr/bin/env python3
"""
ISA Instruction Extractor for MINIX Architecture Analysis

Extracts and analyzes instruction mnemonics from assembly source files
for both i386 and ARM (earm) architectures.

Generates frequency tables, categorization, and JSON output for analysis.
"""

import re
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set

class InstructionExtractor:
    """Base class for instruction extraction from assembly files."""
    
    def __init__(self, arch: str):
        self.arch = arch
        self.instructions = Counter()
        self.categories = defaultdict(list)
        self.addressing_modes = Counter()
        self.files_processed = []
        self.instruction_details = []
        
    def extract_from_file(self, filepath: Path) -> None:
        """Extract instructions from a single assembly file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            self.files_processed.append(str(filepath))
            self._process_content(content)
        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
    
    def _process_content(self, content: str) -> None:
        """Override in subclasses for architecture-specific processing."""
        raise NotImplementedError
    
    def get_top_instructions(self, count: int = 20) -> List[Tuple[str, int]]:
        """Return top N most frequent instructions."""
        return self.instructions.most_common(count)
    
    def export_json(self, output_path: Path) -> None:
        """Export analysis results to JSON."""
        data = {
            'architecture': self.arch,
            'total_instructions': sum(self.instructions.values()),
            'unique_instructions': len(self.instructions),
            'files_processed': len(self.files_processed),
            'files': self.files_processed,
            'instruction_frequencies': dict(self.instructions),
            'top_20_instructions': [{'instruction': instr, 'count': count} 
                                   for instr, count in self.get_top_instructions(20)],
            'categories': {cat: len(instrs) for cat, instrs in self.categories.items()},
            'addressing_modes': dict(self.addressing_modes),
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported analysis to {output_path}")


class I386InstructionExtractor(InstructionExtractor):
    """Extract instructions from i386 assembly files (AT&T syntax)."""
    
    # i386 instruction categories (AT&T syntax)
    INSTRUCTION_CATEGORIES = {
        'movement': ['mov', 'movl', 'movw', 'movb', 'movzx', 'movsx', 'lea'],
        'stack': ['push', 'pushl', 'pop', 'popl', 'pushf', 'popf'],
        'arithmetic': ['add', 'addl', 'sub', 'subl', 'inc', 'incl', 'dec', 'decl',
                      'mul', 'mull', 'div', 'divl', 'imul', 'idiv'],
        'logical': ['and', 'andl', 'or', 'orl', 'xor', 'xorl', 'not', 'neg'],
        'shift': ['shl', 'shll', 'shr', 'shrl', 'sar', 'sarl', 'rol', 'ror',
                 'rcl', 'rcr'],
        'comparison': ['cmp', 'cmpl', 'test', 'testl'],
        'control': ['jmp', 'je', 'jne', 'jz', 'jnz', 'jl', 'jle', 'jg', 'jge',
                   'ja', 'jb', 'jo', 'jno', 'call', 'ret', 'retn', 'leave'],
        'privileged': ['lgdt', 'lidt', 'lldt', 'ltr', 'mov', 'smsw', 'lmsw',
                      'clts', 'invlpg', 'wbinvd', 'invd', 'cli', 'sti', 'hlt',
                      'wrmsr', 'rdmsr', 'cpuid', 'rdtsc', 'sysenter', 'sysexit'],
        'bitwise': ['bt', 'bts', 'btr', 'btc', 'bsf', 'bsr'],
        'string': ['rep', 'repe', 'repne', 'movs', 'movsb', 'movsw', 'movsl',
                  'stosb', 'stosw', 'stosl', 'lodsb', 'lodsw', 'lodsl'],
        'conditional': ['seta', 'setb', 'sete', 'setn', 'setz', 'setnz', 'setl',
                       'setg', 'setle', 'setge'],
        'other': ['nop', 'ud2', 'int', 'iret', 'iretu'],
    }
    
    def __init__(self):
        super().__init__('i386')
        self._build_instruction_map()
    
    def _build_instruction_map(self) -> None:
        """Build quick lookup for instruction categories."""
        self.instruction_map = {}
        for category, instrs in self.INSTRUCTION_CATEGORIES.items():
            for instr in instrs:
                self.instruction_map[instr] = category
    
    def _process_content(self, content: str) -> None:
        """Extract i386 instructions from assembly source (AT&T syntax)."""
        lines = content.split('\n')
        
        for line in lines:
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]
            
            # Skip empty lines and labels
            line = line.strip()
            if not line or line.endswith(':'):
                continue
            
            # Extract mnemonic (first word before space or comma)
            # AT&T syntax: mnemonic dest, src, src2, ...
            match = re.match(r'^(\w+)\b', line)
            if not match:
                continue
            
            mnemonic = match.group(1).lower()
            
            # Categorize instruction
            category = self.instruction_map.get(mnemonic, 'other')
            
            # Count instruction and category
            self.instructions[mnemonic] += 1
            self.categories[category].append(mnemonic)
            
            # Extract addressing mode hint
            self._extract_addressing_mode(line, mnemonic)
    
    def _extract_addressing_mode(self, line: str, mnemonic: str) -> None:
        """Extract addressing mode hints from instruction."""
        # Suffix indicators in AT&T syntax: l (long/32-bit), w (word/16-bit), 
        # b (byte/8-bit), q (quad/64-bit)
        if mnemonic.endswith('l'):
            self.addressing_modes['32-bit'] += 1
        elif mnemonic.endswith('w'):
            self.addressing_modes['16-bit'] += 1
        elif mnemonic.endswith('b'):
            self.addressing_modes['8-bit'] += 1
        elif mnemonic.endswith('q'):
            self.addressing_modes['64-bit'] += 1
        else:
            self.addressing_modes['unknown'] += 1
        
        # Memory access indicators
        if '$' in line:
            self.addressing_modes['immediate'] += 1
        if '%' in line:
            self.addressing_modes['register'] += 1
        if '(' in line:
            self.addressing_modes['memory'] += 1


class ARMInstructionExtractor(InstructionExtractor):
    """Extract instructions from ARM assembly files (A32 syntax)."""
    
    # ARM A32 instruction categories
    INSTRUCTION_CATEGORIES = {
        'movement': ['mov', 'movw', 'movt', 'ldr', 'ldm', 'ldmia', 'ldmdb', 
                    'ldmfd', 'ldmea', 'str', 'stm', 'stmia', 'stmdb', 'stmfd', 'stmea'],
        'arithmetic': ['add', 'adc', 'sub', 'sbc', 'rsb', 'rsc', 'mul', 'mla',
                      'umul', 'umla', 'sdiv', 'udiv'],
        'logical': ['and', 'orr', 'eor', 'bic', 'mvn'],
        'shift': ['lsl', 'lsr', 'asr', 'ror', 'rrx'],
        'comparison': ['cmp', 'cmn', 'tst', 'teq'],
        'control': ['b', 'bl', 'bx', 'blx', 'bxj', 'svc', 'swi'],
        'coprocessor': ['mcr', 'mrc', 'mcrr', 'mrrc', 'cdp', 'cdp2', 'ldc', 'stc'],
        'bit_manipulation': ['clz', 'ctz', 'popcount'],
        'memory': ['pld', 'pli', 'dmb', 'dsb', 'isb'],
        'misc': ['nop', 'wfi', 'wfe', 'sev', 'yield'],
        'other': ['push', 'pop'],
    }
    
    def __init__(self):
        super().__init__('arm')
        self._build_instruction_map()
    
    def _build_instruction_map(self) -> None:
        """Build quick lookup for instruction categories."""
        self.instruction_map = {}
        for category, instrs in self.INSTRUCTION_CATEGORIES.items():
            for instr in instrs:
                self.instruction_map[instr] = category
    
    def _process_content(self, content: str) -> None:
        """Extract ARM instructions from assembly source (A32 syntax)."""
        lines = content.split('\n')
        
        for line in lines:
            # Remove comments (both ; and @)
            for comment_char in [';', '@']:
                if comment_char in line:
                    line = line[:line.index(comment_char)]
            
            # Skip empty lines and labels
            line = line.strip()
            if not line or line.endswith(':'):
                continue
            
            # Extract mnemonic (first word before space or comma)
            # ARM syntax: mnemonic{cond} dst, src, src2, ...
            # Handle conditional suffixes (eq, ne, lt, gt, etc.)
            match = re.match(r'^([a-z]+)(?:[a-z]{2})?\b', line)
            if not match:
                continue
            
            base_mnemonic = match.group(1).lower()
            
            # Try to get base mnemonic without suffix
            mnemonic = base_mnemonic
            for instr in self.instruction_map.keys():
                if line.startswith(instr):
                    mnemonic = instr
                    break
            
            # Categorize instruction
            category = self.instruction_map.get(mnemonic, 'other')
            
            # Count instruction and category
            self.instructions[mnemonic] += 1
            self.categories[category].append(mnemonic)
            
            # Extract addressing mode and conditional
            self._extract_addressing_info(line, mnemonic)
    
    def _extract_addressing_info(self, line: str, mnemonic: str) -> None:
        """Extract addressing information from ARM instruction."""
        # Extract conditional suffix
        conditional_codes = ['eq', 'ne', 'lt', 'le', 'gt', 'ge', 'ls', 'hi', 
                            'cc', 'cs', 'pl', 'mi', 'vc', 'vs', 'al']
        
        found_conditional = False
        for cond in conditional_codes:
            if f"{mnemonic}{cond}" in line:
                self.addressing_modes[f'conditional_{cond}'] += 1
                found_conditional = True
                break
        
        if not found_conditional:
            self.addressing_modes['unconditional'] += 1
        
        # Register operand count hints
        if ',' in line:
            commas = line.count(',')
            self.addressing_modes[f'operands_{commas+1}'] += 1
        
        # Memory access hints
        if '[' in line:
            self.addressing_modes['memory_access'] += 1
        if '#' in line:
            self.addressing_modes['immediate'] += 1


def main():
    """Main entry point for instruction extraction."""
    
    if len(sys.argv) < 2:
        print("Usage: python3 isa_instruction_extractor.py <minix_root> [output_dir]")
        print("  minix_root: Path to MINIX source tree")
        print("  output_dir: Output directory for JSON results (default: ./analysis/)")
        sys.exit(1)
    
    minix_root = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('./analysis/')
    output_dir.mkdir(exist_ok=True)
    
    # Process i386 architecture
    print("Processing i386 architecture...")
    i386_extractor = I386InstructionExtractor()
    i386_arch_dir = minix_root / 'minix' / 'kernel' / 'arch' / 'i386'
    
    if i386_arch_dir.exists():
        for asm_file in i386_arch_dir.glob('*.S'):
            i386_extractor.extract_from_file(asm_file)
            print(f"  Processed: {asm_file.name}")
    else:
        print(f"  Warning: i386 architecture directory not found at {i386_arch_dir}")
    
    # Export i386 results
    i386_output = output_dir / 'i386_instructions.json'
    i386_extractor.export_json(i386_output)
    
    print(f"\ni386 Summary:")
    print(f"  Total instructions: {sum(i386_extractor.instructions.values())}")
    print(f"  Unique mnemonics: {len(i386_extractor.instructions)}")
    print(f"  Files processed: {len(i386_extractor.files_processed)}")
    print(f"  Top 10 instructions:")
    for instr, count in i386_extractor.get_top_instructions(10):
        print(f"    {instr:12} {count:6} ({100*count/sum(i386_extractor.instructions.values()):5.1f}%)")
    
    # Process ARM architecture
    print("\nProcessing ARM (earm) architecture...")
    arm_extractor = ARMInstructionExtractor()
    arm_arch_dir = minix_root / 'minix' / 'kernel' / 'arch' / 'earm'
    
    if arm_arch_dir.exists():
        for asm_file in arm_arch_dir.glob('*.S'):
            arm_extractor.extract_from_file(asm_file)
            print(f"  Processed: {asm_file.name}")
    else:
        print(f"  Warning: ARM architecture directory not found at {arm_arch_dir}")
    
    # Export ARM results
    arm_output = output_dir / 'arm_instructions.json'
    arm_extractor.export_json(arm_output)
    
    print(f"\nARM Summary:")
    print(f"  Total instructions: {sum(arm_extractor.instructions.values())}")
    print(f"  Unique mnemonics: {len(arm_extractor.instructions)}")
    print(f"  Files processed: {len(arm_extractor.files_processed)}")
    print(f"  Top 10 instructions:")
    for instr, count in arm_extractor.get_top_instructions(10):
        print(f"    {instr:12} {count:6} ({100*count/sum(arm_extractor.instructions.values()):5.1f}%)")
    
    # Summary comparison
    print(f"\nComparison:")
    print(f"  i386 total:   {sum(i386_extractor.instructions.values())} instructions")
    print(f"  ARM total:    {sum(arm_extractor.instructions.values())} instructions")
    print(f"  i386 unique:  {len(i386_extractor.instructions)} mnemonics")
    print(f"  ARM unique:   {len(arm_extractor.instructions)} mnemonics")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

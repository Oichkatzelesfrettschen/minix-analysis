#!/usr/bin/env python3
"""
Data-Driven TikZ Diagram Generator
Creates TikZ diagrams from analyzed MINIX source data
"""

import json
import argparse
import math
from pathlib import Path

class TikZGenerator:
    def __init__(self, data_dir="diagrams/data"):
        self.data_dir = Path(data_dir)
        self.load_all_data()

    def load_all_data(self):
        """Load all JSON data files"""
        self.kernel_data = self.load_json("kernel_structure.json")
        self.process_data = self.load_json("process_table.json")
        self.memory_data = self.load_json("memory_layout.json")
        self.ipc_data = self.load_json("ipc_system.json")
        self.boot_data = self.load_json("boot_sequence.json")
        self.stats = self.load_json("statistics.json")

    def load_json(self, filename):
        """Load a JSON file"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}

    def generate_syscall_table_tikz(self):
        """Generate system call table diagram from actual data"""
        tex = r"""\documentclass{standalone}
\usepackage{tikz}
\usepackage{array}
\usetikzlibrary{shapes,arrows,positioning,calc}

\begin{document}
\begin{tikzpicture}

% Title
\node[font=\Large\bfseries] at (0, 0) {MINIX System Call Table};
\node[font=\normalsize] at (0, -0.5) {""" + f"Total: {self.stats.get('total_syscalls', 0)} system calls" + r"""};

% Create table
\node at (0, -1.5) {
\begin{tabular}{|l|l|r|}
\hline
\textbf{System Call} & \textbf{Source File} & \textbf{Lines} \\
\hline
"""
        # Add actual system calls from data
        for i, syscall in enumerate(self.kernel_data.get('system_calls', [])[:15]):
            name = syscall['name'].replace('_', ' ')  # Replace underscore with space
            file = syscall['file'].replace('minix/kernel/system/', '').replace('_', r'\_')
            lines = syscall['line_count']
            tex += f"{name} & {file} & {lines} \\\\\n"
            if i < 14:
                tex += r"\hline" + "\n"

        tex += r"""\hline
\end{tabular}
};

% Statistics box
\node[draw=black, fill=yellow!10, minimum width=6cm, minimum height=1.5cm] at (0, -10) {
\begin{tabular}{ll}
\textbf{Kernel Files:} & """ + str(self.stats.get('kernel_files', 0)) + r""" \\
\textbf{Kernel Lines:} & """ + str(self.stats.get('kernel_lines', 0)) + r""" \\
\textbf{Total Servers:} & """ + str(self.stats.get('server_count', 0)) + r""" \\
\textbf{Total Drivers:} & """ + str(self.stats.get('driver_count', 0)) + r"""
\end{tabular}
};

\end{tikzpicture}
\end{document}"""
        return tex

    def generate_process_states_tikz(self):
        """Generate process state diagram from actual data"""
        tex = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,automata}

\begin{document}
\begin{tikzpicture}[
    state/.style={rectangle, draw=black, fill=blue!20, minimum width=2.5cm, minimum height=1cm},
    arrow/.style={->, >=stealth, thick}
]

% Title
\node[font=\Large\bfseries] at (0, 8) {MINIX Process States};
\node[font=\normalsize] at (0, 7.5) {From proc.h analysis};

"""
        # Add actual process states from data
        states = self.process_data.get('process_states', [])

        # Position states in a circle
        num_states = min(len(states), 8)  # Limit to 8 for layout
        for i, state_info in enumerate(states[:num_states]):
            angle = 360 * i / num_states
            x = 4 * math.cos(angle * 3.14159 / 180)
            y = 4 * math.sin(angle * 3.14159 / 180)

            state_name = state_info['state'].replace('RTS_', '').replace('_', ' ')
            desc = state_info['description'][:20] if len(state_info['description']) > 20 else state_info['description']

            tex += f"\\node[state] (s{i}) at ({x:.2f}, {y:.2f}) {{{state_name}}};\n"
            tex += f"\\node[font=\\footnotesize, below] at (s{i}.south) {{{desc}}};\n\n"

        # Add process table info
        tex += r"""
% Process Table Info
\node[draw=black, fill=green!10, minimum width=8cm] at (0, -6) {
\begin{tabular}{ll}
\textbf{Max Processes:} & """ + str(self.process_data.get('max_processes', 'N/A')) + r""" \\
\textbf{Process Fields:} & """ + str(len(self.process_data.get('process_fields', []))) + r""" fields \\
\textbf{Scheduling Queues:} & """ + str(len(self.process_data.get('scheduling_queues', []))) + r""" priority levels
\end{tabular}
};

\end{tikzpicture}
\end{document}"""
        return tex

    def generate_boot_sequence_tikz(self):
        """Generate boot sequence from actual data"""
        tex = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,calc}

\begin{document}
\begin{tikzpicture}[
    box/.style={rectangle, draw=black, fill=blue!20, minimum width=3cm, minimum height=0.8cm},
    arrow/.style={->, >=stealth, thick}
]

% Title
\node[font=\Large\bfseries] at (0, 0) {MINIX Boot Sequence};
\node[font=\normalsize] at (0, -0.5) {From main.c analysis};

"""
        # Add actual boot stages from data
        stages = self.boot_data.get('boot_stages', [])
        y_pos = -2

        for i, stage in enumerate(stages[:15]):  # Limit to 15 stages
            stage_clean = stage.replace('_', ' ')  # Replace underscores
            tex += f"\\node[box] (stage{i}) at (0, {y_pos}) {{{stage_clean}()}};\n"
            if i > 0:
                tex += f"\\draw[arrow] (stage{i-1}) -- (stage{i});\n"
            y_pos -= 1

        # Add initialization functions info
        init_funcs = self.boot_data.get('initialization_functions', [])
        if init_funcs:
            tex += f"""
% Initialization Functions
\\node[draw=black, fill=yellow!10, align=left] at (5, -5) {{
\\textbf{{Init Functions:}}\\\\
"""
            for func in init_funcs[:5]:
                func_clean = func.replace('_', ' ')
                tex += f"{func_clean}()\\\\\\\\"
            tex += "};\n"

        tex += r"""
\end{tikzpicture}
\end{document}"""
        return tex

    def generate_ipc_architecture_tikz(self):
        """Generate IPC architecture from actual data"""
        tex = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,calc}

\begin{document}
\begin{tikzpicture}[
    endpoint/.style={rectangle, draw=black, fill=green!20, minimum width=2cm, minimum height=0.8cm},
    arrow/.style={<->, >=stealth, thick}
]

% Title
\node[font=\Large\bfseries] at (0, 8) {MINIX IPC Architecture};
\node[font=\normalsize] at (0, 7.5) {Message Passing System};

"""
        # Add endpoints from data
        endpoints = self.ipc_data.get('endpoints', [])

        # Kernel endpoints
        kernel_endpoints = [e for e in endpoints if 'KERNEL' in e['name'] or 'SYSTEM' in e['name']]
        server_endpoints = [e for e in endpoints if 'PM' in e['name'] or 'VFS' in e['name'] or 'VM' in e['name']]

        # Draw kernel
        tex += "\\node[endpoint, fill=red!20, minimum width=3cm] (kernel) at (0, 5) {KERNEL};\n"

        # Draw servers in a row
        x_pos = -4
        for i, endpoint in enumerate(server_endpoints[:5]):
            name = endpoint['name'].replace('_PROC_NR', '').replace('_', ' ')
            tex += f"\\node[endpoint] (ep{i}) at ({x_pos}, 2) {{{name}}};\n"
            tex += f"\\draw[arrow] (kernel) -- (ep{i});\n"
            x_pos += 2

        # Add IPC functions
        funcs = self.ipc_data.get('ipc_functions', [])[:5]
        if funcs:
            tex += """
% IPC Functions
\\node[draw=black, fill=yellow!10, align=left] at (0, -1) {
\\textbf{IPC Functions:}\\\\
"""
            for func in funcs:
                func_clean = func.replace('_', ' ')
                tex += f"{func_clean}()\\\\\\\\"
            tex += "};\n"

        # Add message info
        tex += f"""
% Message Info
\\node[draw=black, fill=blue!10] at (0, -3) {{
Message Size: {self.ipc_data.get('message_size', 'Unknown')}
}};
"""

        tex += r"""
\end{tikzpicture}
\end{document}"""
        return tex

    def generate_memory_regions_tikz(self):
        """Generate memory regions from actual data"""
        tex = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,calc,patterns}

\begin{document}
\begin{tikzpicture}[
    region/.style={rectangle, draw=black, minimum width=4cm, minimum height=0.8cm},
    arrow/.style={->, >=stealth}
]

% Title
\node[font=\Large\bfseries] at (0, 10) {MINIX Memory Regions};
\node[font=\normalsize] at (0, 9.5) {From VM server analysis};

% Memory layout
\draw[thick] (0, 0) rectangle (4, 8);

"""
        # Add memory regions from data
        regions = self.memory_data.get('memory_regions', [])
        unique_regions = list(set(regions))[:8]  # Get unique regions, limit to 8

        y_pos = 7
        height = 8.0 / max(len(unique_regions), 1)

        for i, region in enumerate(unique_regions):
            # Different colors for different region types
            if 'STACK' in region:
                color = 'blue!20'
            elif 'HEAP' in region:
                color = 'green!20'
            elif 'TEXT' in region:
                color = 'red!20'
            else:
                color = 'gray!20'

            region_clean = region.replace('_', ' ')
            tex += f"\\node[region, fill={color}] at (2, {y_pos}) {{{region_clean}}};\n"
            y_pos -= height

        # Add memory constants
        tex += f"""
% Memory Constants
\\node[draw=black, fill=yellow!10, align=left] at (7, 4) {{
\\textbf{{Memory Configuration:}}\\\\
Page Size: {self.memory_data.get('page_size', 'Unknown')}\\\\
Kernel Base: {self.memory_data.get('kernel_base', 'Unknown')}\\\\
Total Regions: {len(unique_regions)}
}};
"""

        tex += r"""
\end{tikzpicture}
\end{document}"""
        return tex

    def save_all_tikz_files(self, output_dir="diagrams/tikz-generated"):
        """Save all generated TikZ files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        diagrams = {
            "syscall-table": self.generate_syscall_table_tikz(),
            "process-states": self.generate_process_states_tikz(),
            "boot-sequence-data": self.generate_boot_sequence_tikz(),
            "ipc-architecture": self.generate_ipc_architecture_tikz(),
            "memory-regions": self.generate_memory_regions_tikz()
        }

        for name, content in diagrams.items():
            filepath = output_path / f"{name}.tex"
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Generated: {filepath}")

        return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate TikZ diagrams from MINIX data")
    parser.add_argument("--data-dir", default="diagrams/data",
                      help="Directory containing JSON data files")
    parser.add_argument("--output", default="diagrams/tikz-generated",
                      help="Output directory for TikZ files")
    args = parser.parse_args()

    generator = TikZGenerator(args.data_dir)
    generator.save_all_tikz_files(args.output)
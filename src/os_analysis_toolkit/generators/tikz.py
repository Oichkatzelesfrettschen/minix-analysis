"""
TikZ diagram generator for LaTeX output
"""

from typing import Dict, Any
from .base import DiagramGenerator


from pathlib import Path


class TikZGenerator(DiagramGenerator):
    """Generate TikZ/LaTeX diagrams from analyzed data"""

    def __init__(self, output_dir: str = "diagrams", template_dir: str = "src/os_analysis_toolkit/templates"):
        """Initialize TikZ generator"""
        super().__init__(output_dir)
        self.template_dir = Path(template_dir)

    def _load_template(self, template_name: str) -> str:
        """Load a LaTeX template file."""
        template_path = self.template_dir / template_name
        return template_path.read_text()

    def generate_kernel_diagram(self, data: Dict[str, Any]) -> str:
        """Generate kernel architecture diagram in TikZ"""
        template = self._load_template("kernel_diagram.tex")

        nodes = []
        connections = []
        labels = []

        # Default data if not provided
        # Example: Populate nodes
        nodes.append("\\node[box, fill=red!20] (hw) at (0,0) {Hardware};")
        nodes.append("\\node[box, fill=orange!20] (kernel) at (0,2) {Microkernel};")
        nodes.append("\\node[box, fill=yellow!20] (servers) at (0,4) {System Servers};")
        nodes.append("\\node[box, fill=green!20] (drivers) at (4,4) {Device Drivers};")
        nodes.append("\\node[box, fill=blue!20] (apps) at (0,6) {Applications};")

        # Example: Populate connections
        connections.append("\\draw[arrow] (hw) -- (kernel);")
        connections.append("\\draw[arrow] (kernel) -- (servers);")
        connections.append("\\draw[arrow] (kernel) -- (drivers);")
        connections.append("\\draw[arrow] (servers) -- (apps);")

        # Example: Populate labels
        labels.append("\\node[right] at (6,0) {Physical Layer};")
        labels.append("\\node[right] at (6,2) {Core Services};")
        labels.append("\\node[right] at (6,4) {System Services};")
        labels.append("\\node[right] at (6,6) {User Space};")

        tikz_output = template.replace("{{nodes}}", "\n".join(nodes))
        tikz_output = tikz_output.replace("{{connections}}", "\n".join(connections))
        tikz_output = tikz_output.replace("{{labels}}", "\n".join(labels))

        return tikz_output

    def generate_fork_diagram(self, data: Dict[str, Any]) -> str:
        """Generate fork/process creation sequence diagram in TikZ from data."""
        template = self._load_template("fork_diagram.tex")

        # Prepare dynamic content
        nodes = []
        arrows = []
        annotations = []
        cpu_context_lines = []

        # Example: Populate nodes (this logic will be expanded later)
        processes = data.get("processes", [])
        for proc in processes:
            if proc["name"] == "Parent":
                nodes.append(f"\\node[box, fill={proc["color"]}] ({proc["name"].lower()}) at (1,0) {{{proc["label"]}}};")
            elif proc["name"] == "Child":
                nodes.append(f"\\node[box, fill={proc["color"]}] ({proc["name"].lower()}) at (5,0) {{{proc["label"]}}};")

        # Example: Populate arrows
        actions = data.get("actions", [])
        for action in actions:
            arrow_style = "arrow, dashed" if action.get("dashed") else "arrow"
            if action.get("label"): # Check if label exists before adding it
                arrows.append(f"\\draw[{arrow_style}] ({action["from"].lower()}) -- node[label, {'right' if action['from'] == 'lib' else 'above'}] {{{action["label"]}}} ({action["to"].lower()});")
            else:
                arrows.append(f"\\draw[{arrow_style}] ({action["from"].lower()}) -- ({action["to"].lower()});")

        # Example: Populate annotations
        annotations_data = data.get("annotations", [])
        for ann in annotations_data:
            annotations.append(f"\\node[label] at ({ann["at"]}) {{{ann["label"]}}};")

        # Example: Populate CPU context
        cpu_context_data = data.get("cpu_context", [])
        for i, ctx in enumerate(cpu_context_data):
            cpu_context_lines.append(f"\\node[label, anchor=west] at (0,{{-6.7 - {i} * 0.4}}) {{{ctx}}};")


        # Replace placeholders in the template
        tikz_output = template.replace("{{nodes}}", "\n".join(nodes))
        tikz_output = tikz_output.replace("{{arrows}}", "\n".join(arrows))
        tikz_output = tikz_output.replace("{{annotations}}", "\n".join(annotations))
        tikz_output = tikz_output.replace("{{cpu_context}}", "\n".join(cpu_context_lines))

        return tikz_output


    def generate_memory_diagram(self, data: Dict[str, Any]) -> str:
        """Generate memory layout diagram in TikZ from data."""
        # Default data if not provided
        segments = data.get("memory_segments", [
            {"name": "low_mem", "label": "Kernel\\\\0x00000000\\\\\\[-2mm]\\\\...\\\\\\[-2mm]\\\\0x007FFFFF", "fill": "yellow!30", "height": "3cm", "at": "(0,-1.5)"},
            {"name": "free_modules", "label": "Free/Modules\\\\0x00800000\\\\\\[-2mm]\\\\...\\\\\\[-2mm]\\\\0x7FFFFFFF", "fill": "white", "height": "2cm", "at": "(0,-4.7)"},
            {"name": "user_app", "label": "User App\\\\0x08000000\\\\\\[-2mm]\\\\...\\\\\\[-2mm]\\\\0x7FFFFFFF", "fill": "white", "height": "1.5cm", "at": "(2.5,-1.5)"},
            {"name": "kernel_high", "label": "Kernel\\\\0x80000000\\\\\\[-2mm]\\\\...\\\\\\[-2mm]\\\\0x80FFFFFF", "fill": "yellow!30", "height": "1cm", "at": "(2.5,-3.1)"},
            {"name": "free_high", "label": "Free\\\\0x81000000\\\\\\[-2mm]\\\\...\\\\\\[-2mm]\\\\0xFFFFFFFF", "fill": "white", "height": "1cm", "at": "(2.5,-4.2)"}
        ])
        annotations = data.get("annotations", [
            {"at": "(4.8,-1.8)", "label": "1:1 mapping"},
            {"at": "(4.8,-2.8)", "label": "Remapped to high\\\\address"}
        ])

        tikz_nodes = []
        tikz_annotations = []

        # Title
        tikz_nodes.append("\\\\node[font=\\\\large\\\\bfseries] at (2,-0.5) {MINIX Memory Layout (32-bit x86)};")

        # Virtual address space (before paging)
        tikz_nodes.append("\\\\node[font=\\\\small\\\\bfseries, anchor=north east] at (1,-1) {Virtual Memory (Phase 1)};")

        # Virtual address space (after paging - Phase 2+)
        tikz_nodes.append("\\\\node[font=\\\\small\\\\bfseries, anchor=north east] at (4,-1) {Virtual Memory (Phase 2+)};")

        for segment in segments:
            tikz_nodes.append(f"\\\\node[mem, fill={segment["fill"]}, minimum height={segment["height"]}, anchor=north west] ({segment["name"]}) at {segment["at"]} {{{segment["label"]}}};")

        for ann in annotations:
            tikz_annotations.append(f"\\\\node[label, anchor=west] at {ann["at"]} {{{ann["label"]}}};")

        tikz = f"""\\documentclass[tikz,border=5pt]{{standalone}}
\\usepackage{{tikz}}
\\usepackage{{times}}
\\usetikzlibrary{{shapes,arrows,positioning}}

\\begin{{document}}
\\begin{{tikzpicture}}[
    mem/.style={{rectangle, minimum width=2cm, draw=black, font=\\small}},
    label/.style={{font=\\tiny}}
]

% Nodes
{'\\n'.join(node.replace('\\n', '\\\\') for node in tikz_nodes)}

% Annotations
{'\\n'.join(ann.replace('\\n', '\\\\') for ann in tikz_annotations)}

\\end{{tikzpicture}}
\\end{{document}}"""
        return tikz


    def generate_ipc_diagram(self, data: Dict[str, Any]) -> str:
        """Generate IPC flow diagram in TikZ from data."""
        # Default data if not provided
        processes = data.get("processes", [
            {"name": "Sender", "label": "Sender\\\\Ring 3", "color": "sendercolor", "at": "(1,0)"},
            {"name": "Kernel", "label": "Kernel\\\\Ring 0", "color": "kernelcolor", "at": "(5,0)"},
            {"name": "Receiver", "label": "Receiver\\\\Ring 3", "color": "receivercolor", "at": "(9,0)"}
        ])
        message_flow = data.get("message_flow", [
            {"from": "Sender", "to": "Kernel", "label": "1. INT 0x30\\\\SEND"},
            {"from": "Kernel", "to": "Receiver", "label": "2. Copy msg\\\\Validate"}
        ])
        return_path = data.get("return_path", [
            {"from": "Receiver", "to": "Kernel", "label": "3. RECEIVE\\\\Process", "dashed": True},
            {"from": "Kernel", "to": "Sender", "label": "4. Return ctrl", "dashed": True}
        ])
        state_annotations = data.get("state_annotations", [
            {"at": "Sender.south", "label": "Message ready"},
            {"at": "Kernel.south", "label": "Routing"},
            {"at": "Receiver.south", "label": "Blocked wait"}
        ])
        timeline_labels = data.get("timeline_labels", [
            {"at": "1,-2.8", "label": "SEND"},
            {"at": "5,-2.8", "label": "COPY"},
            {"at": "9,-2.8", "label": "RECV"}
        ])

        tikz_nodes = []
        tikz_message_flow = []
        tikz_return_path = []
        tikz_state_annotations = []
        tikz_timeline_labels = []

        # Define colors
        tikz_nodes.append("\\\\definecolor{sendercolor}{RGB}{52,152,219}")
        tikz_nodes.append("\\\\definecolor{receivercolor}{RGB}{46,204,113}")
        tikz_nodes.append("\\\\definecolor{kernelcolor}{RGB}{230,126,34}")

        # Title
        tikz_nodes.append("\\\\node[font=\\\\large\\\\bfseries] at (5,-0.5) {MINIX IPC Message Flow};")

        # Processes
        for proc in processes:
            tikz_nodes.append(f"\\\\node[proc, fill={proc["color"]}] ({proc["name"].lower()}) at {proc["at"]} {{{proc["label"]}}};")

        # Message flow
        for flow in message_flow:
            tikz_message_flow.append(f"\\\\draw[arrow] ({flow["from"].lower()}) -- node[label, above] {{{flow["label"]}}} ({flow["to"].lower()});")

        # Return path
        for path in return_path:
            style = "arrow, dashed" if path.get("dashed") else "arrow"
            tikz_return_path.append(f"\\\\draw[{style}] ({path["from"].lower()}) -- node[label, below] {{{path["label"]}}} ({path["to"].lower()});")

        # State annotations
        for ann in state_annotations:
            tikz_state_annotations.append(f"\\\\node[label, below] at ({ann["at"]}) {{{ann["label"]}}};")

        # Timeline
        tikz_nodes.append("\\\\node[font=\\\\tiny\\\\bfseries] at (5,-2) {IPC Timing};")
        tikz_nodes.append("\\\\draw[thick] (0.5,-2.5) -- (9.5,-2.5);")
        for label in timeline_labels:
            tikz_timeline_labels.append(f"\\\\node[label] at {label["at"]} {{{label["label"]}}};")

        tikz = f"""\\documentclass[tikz,border=5pt]{{standalone}}
\\usepackage{{tikz}}
\\usepackage{{times}}
\\usetikzlibrary{{shapes,arrows,positioning}}

{'\\n'.join(tikz_nodes[:3])} % Colors

\\begin{{document}}
\\begin{{tikzpicture}}[
    proc/.style={{rectangle, minimum width=2cm, minimum height=1cm, draw=black}},
    arrow/.style={{->, thick}},
    label/.style={{font=\\small}}
]

% Title and Processes
{'\\n'.join(node.replace('\\n', '\\\\') for node in tikz_nodes[3:])}

% Message flow
{'\\n'.join(flow.replace('\\n', '\\\\') for flow in tikz_message_flow)}

% Return path
{'\\n'.join(path.replace('\\n', '\\\\') for path in tikz_return_path)}

% State annotations
{'\\n'.join(ann.replace('\\n', '\\\\') for ann in tikz_state_annotations)}

% Timeline labels
{'\\n'.join(label.replace('\\n', '\\\\') for label in tikz_timeline_labels)}

\\end{{tikzpicture}}
\\end{{document}}"""
        return tikz

    def generate_boot_diagram(self, data: Dict[str, Any]) -> str:
        """Generate boot sequence diagram in TikZ from data."""
        stages = data.get("boot_stages", [])
        connections = data.get("boot_connections", [])
        descriptions = data.get("boot_descriptions", {})

        tikz_nodes = []
        tikz_connections = []
        tikz_descriptions = []

        # Define colors for stages (can be dynamic based on stage type or status)
        colors = ["red!20", "orange!20", "yellow!20", "green!20", "blue!20", "purple!20"]

        # Generate nodes for stages
        for i, stage_info in enumerate(stages):
            stage_name = stage_info["name"].replace(" ", "")  # Sanitize for TikZ node name
            stage_label = stage_info["label"]
            fill_color = colors[i % len(colors)]
            if i == 0:
                tikz_nodes.append(f"    \\node[stage, fill={fill_color}] ({stage_name}) {{{stage_label}}};")
            else:
                prev_stage_name = stages[i-1]["name"].replace(" ", "")
                tikz_nodes.append(f"    \\node[stage, fill={fill_color}, below=of {prev_stage_name}] ({stage_name}) {{{stage_label}}};")

            if stage_name in descriptions:
                # Assuming description for node is placed to its right
                tikz_descriptions.append(f"\\node[right=1cm of {stage_name}] {{{descriptions[stage_name]}}};")


        # Generate connections
        for conn in connections:
            from_stage = conn["from"].replace(" ", "")
            to_stage = conn["to"].replace(" ", "")
            tikz_connections.append(f"\\draw[arrow] ({from_stage}) -- ({to_stage});")

        tikz = f"""\\documentclass[tikz,border=10pt]{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{chains,positioning}}

\\begin{{document}}
\\begin{{tikzpicture}}[
    stage/.style={{rectangle, draw, minimum width=3cm, minimum height=1cm, on chain}},
    arrow/.style={{->, thick}}
]

% Boot stages
\\begin{{scope}}[start chain=going below, node distance=5mm]
{'\\n'.join(node.replace('\\n', '\\\\') for node in tikz_nodes)}
\\end{{scope}}

% Descriptions
{'\\n'.join(desc.replace('\\n', '\\\\') for desc in tikz_descriptions)}

% Connections
{'\\n'.join(conn.replace('\\n', '\\\\') for conn in tikz_connections)}

\\end{{tikzpicture}}
\\end{{document}}"""
        return tikz


    def generate_process_diagram(self, data: Dict[str, Any]) -> str:
        """Generate a placeholder process diagram."""
        tikz = f"""\\documentclass[tikz,border=10pt]{{standalone}}
\\usepackage{{tikz}}
\\usetikzlibrary{{shapes,arrows,positioning}}

\\begin{{document}}
\\begin{{tikzpicture}}[
    process/.style={{rectangle, draw, fill=blue!20, minimum width=3cm, minimum height=1cm}},
    arrow/.style={{->, thick}}
]

\\node[process] (p1) {{Process 1}};
\\node[process, right=of p1] (p2) {{Process 2}};

\\draw[arrow] (p1) -- (p2);

\\end{{tikzpicture}}
\\end{{document}}"""
        return tikz
        return tikz


    def write_tikz_file(self, filename: str, content: str) -> str:
        """Write TikZ content to a .tex file."""
        print(f"--- START {filename} ---\n{content}\n--- END {filename} ---")
        # filepath = self.output_dir / filename
        # filepath.write_text(content)
        return filename # Return filename for consistency, though it's not used for file path anymore

    def compile_to_pdf(self, tex_file: str) -> bool:
        """
        Compile TikZ diagram to PDF

        Args:
            tex_file: Path to .tex file

        Returns:
            True if compilation successful
        """
        import subprocess
        from pathlib import Path

        print(f"Compiling {tex_file} to PDF...")
        tex_path = Path(tex_file)
        try:
            # Run pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=tex_path.parent,
                capture_output=True,
                text=True
            )
            print(f"pdflatex return code: {result.returncode}")
            print(f"pdflatex stdout: {result.stdout}")
            print(f"pdflatex stderr: {result.stderr}")
            return result.returncode == 0
        except FileNotFoundError:
            print("pdflatex not found - please install texlive")
            return False

    def convert_to_png(self, pdf_file: str, dpi: int = 300) -> bool:
        """
        Convert PDF to PNG

        Args:
            pdf_file: Path to PDF file
            dpi: Resolution for PNG

        Returns:
            True if conversion successful
        """
        import subprocess
        from pathlib import Path

        print(f"Converting {pdf_file} to PNG: {png_path}...")
        pdf_path = Path(pdf_file)
        png_path = pdf_path.with_suffix('.png')

        try:
            # Use ImageMagick's magick command
            result = subprocess.run(
                ["magick", "-density", str(dpi), pdf_file, png_path],
                capture_output=True,
                text=True
            )
            print(f"magick return code: {result.returncode}")
            print(f"magick stdout: {result.stdout}")
            print(f"magick stderr: {result.stderr}")
            return result.returncode == 0
        except FileNotFoundError:
            print("ImageMagick not found - please install imagemagick")
            return False
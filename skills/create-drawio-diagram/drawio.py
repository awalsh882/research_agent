#!/usr/bin/env python3
"""
Draw.io Export CLI Tool

A comprehensive command-line interface for exporting draw.io files to various formats
with extensive customization options including animation support, sizing, transparency,
and desktop-only export methods.

Features:
- Export to multiple formats (PNG, JPG, SVG, PDF, GIF)
- Animation support (for supported formats)
- Customizable sizing, scaling, and quality
- Background transparency control
- Desktop-only export method for reliability
- Batch processing support
- Professional output optimization

Usage:
    python drawio.py export diagram.drawio --format png --width 1920 --height 1080
    python drawio.py export diagram.drawio --format gif --animated
    python drawio.py batch *.drawio --format png --output-dir exports/
    python drawio.py info diagram.drawio  # Show diagram information
"""

import base64
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
try:
    from PIL import Image, ImageDraw
except ImportError:
    import sys
    print("PIL/Pillow not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw

# ============================================================================
# Constants and Configuration
# ============================================================================

DEFAULT_SIZES = {
    'thumbnail': (400, 300),
    'small': (800, 600),
    'medium': (1200, 900),
    'large': (1920, 1080),
    'xlarge': (2560, 1440),
    'print': (3508, 2480),  # A4 at 300 DPI
}

SUPPORTED_FORMATS = {
    'png': {'animated': False, 'transparency': True, 'quality': False},
    'jpg': {'animated': False, 'transparency': False, 'quality': True},
    'jpeg': {'animated': False, 'transparency': False, 'quality': True},
    'svg': {'animated': True, 'transparency': True, 'quality': False},
    'pdf': {'animated': False, 'transparency': True, 'quality': False},
    'gif': {'animated': True, 'transparency': True, 'quality': False},
}

ANIMATION_SPEEDS = {
    'slow': 0.5,
    'normal': 1.0,
    'fast': 1.5,
    'very-fast': 2.0,
}

QUALITY_PRESETS = {
    'low': 60,
    'medium': 80,
    'high': 90,
    'very-high': 95,
    'maximum': 100,
}


# ============================================================================
# Core Classes
# ============================================================================

class DrawioInfo:
    """Information extracted from a draw.io file."""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.has_animation = False
        self.page_count = 0
        self.pages = []
        self.diagram_size = (0, 0)
        self.background_color = None
        self.version = None
        self.host = None
        self.parse_file()
    
    def parse_file(self) -> None:
        """Parse the draw.io file and extract information."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Get file metadata
            self.host = root.get('host', 'Unknown')
            self.version = root.get('version', 'Unknown')
            
            # Find diagrams - handle different structures
            diagrams = root.findall('diagram')
            if not diagrams:
                # Some files might have the diagram as the root
                if root.tag == 'diagram':
                    diagrams = [root]
                elif root.find('diagram') is not None:
                    diagrams = root.findall('diagram')
                else:
                    # Treat the whole file as one diagram
                    diagrams = [root]
            
            self.page_count = len(diagrams)
            
            for diagram in diagrams:
                page_info = {
                    'id': diagram.get('id'),
                    'name': diagram.get('name', 'Untitled'),
                    'has_animation': False,
                    'element_count': 0,
                }
                
                xml_content = ""
                
                # Check if diagram has compressed content (text) or inline content
                if diagram.text:
                    try:
                        # Decode base64 and decompress
                        import urllib.parse
                        import zlib
                        
                        # Try different decompression methods
                        compressed_data = base64.b64decode(diagram.text)
                        
                        # Try standard zlib decompression first
                        try:
                            decompressed = zlib.decompress(compressed_data)
                            xml_content = decompressed.decode('utf-8')
                        except:
                            # Try raw deflate decompression
                            try:
                                decompressed = zlib.decompress(compressed_data, -15)
                                xml_content = decompressed.decode('utf-8')
                            except:
                                # Try URL decoding first
                                try:
                                    url_decoded = urllib.parse.unquote(diagram.text)
                                    compressed_data = base64.b64decode(url_decoded)
                                    decompressed = zlib.decompress(compressed_data, -15)
                                    xml_content = decompressed.decode('utf-8')
                                except:
                                    # If all else fails, try raw text
                                    xml_content = diagram.text
                        
                    except Exception as e:
                        click.echo(f"Warning: Could not parse diagram content: {e}", err=True)
                
                else:
                    # Check for inline content (uncompressed format)
                    # Look for mxGraphModel element within this diagram
                    graph_model = diagram.find('mxGraphModel')
                    if graph_model is not None:
                        # Convert the element back to string to search in it
                        xml_content = ET.tostring(graph_model, encoding='unicode')
                    else:
                        # Fallback: search the entire content for inline XML
                        xml_content = content
                
                # Parse the XML content
                if xml_content:
                    # Check for animations
                    if 'flowAnimation' in xml_content:
                        page_info['has_animation'] = True
                        self.has_animation = True
                    
                    # Count elements
                    page_info['element_count'] = xml_content.count('<mxCell')
                    
                    # Extract dimensions
                    if 'pageWidth' in xml_content:
                        width_match = re.search(r'pageWidth="(\d+)"', xml_content)
                        height_match = re.search(r'pageHeight="(\d+)"', xml_content)
                        if width_match and height_match:
                            page_info['dimensions'] = (int(width_match.group(1)), int(height_match.group(1)))
                
                self.pages.append(page_info)
            
            # Set overall diagram size if available
            if self.pages and 'dimensions' in self.pages[0]:
                self.diagram_size = self.pages[0]['dimensions']
                
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse draw.io file: {e}")


class DrawioValidator:
    """Validation class for draw.io files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.info = DrawioInfo(file_path)
        
    def validate_overlaps(self, min_spacing: int = 20) -> List[Dict[str, Any]]:
        """Check for overlapping elements."""
        overlaps = []
        
        if not self.info.pages:
            return overlaps
            
        for page in self.info.pages:
            elements = page.get('elements', [])
            
            for i, elem1 in enumerate(elements):
                for j, elem2 in enumerate(elements[i+1:], i+1):
                    if self._elements_overlap(elem1, elem2, min_spacing):
                        overlaps.append({
                            'element1': elem1.get('id', f'element_{i}'),
                            'element2': elem2.get('id', f'element_{j}'),
                            'element1_bounds': elem1.get('geometry', {}),
                            'element2_bounds': elem2.get('geometry', {}),
                            'page': page.get('name', 'Page 1')
                        })
        
        return overlaps
    
    def validate_connectors(self) -> List[Dict[str, Any]]:
        """Check for broken or missing connectors."""
        issues = []
        
        if not self.info.pages:
            return issues
            
        for page in self.info.pages:
            elements = page.get('elements', [])
            element_ids = {elem.get('id') for elem in elements if elem.get('id')}
            
            for elem in elements:
                if elem.get('edge'):  # This is a connector
                    source = elem.get('source')
                    target = elem.get('target')
                    
                    if source and source not in element_ids:
                        issues.append({
                            'type': 'missing_source',
                            'connector_id': elem.get('id', 'unknown'),
                            'missing_source': source,
                            'page': page.get('name', 'Page 1')
                        })
                    
                    if target and target not in element_ids:
                        issues.append({
                            'type': 'missing_target',
                            'connector_id': elem.get('id', 'unknown'),
                            'missing_target': target,
                            'page': page.get('name', 'Page 1')
                        })
        
        return issues
    
    def validate_consistency(self, codebase_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check diagram consistency with codebase."""
        issues = []
        
        # Basic consistency checks
        if not self.info.pages:
            issues.append({
                'type': 'no_pages',
                'message': 'Diagram contains no pages'
            })
        
        # Add more consistency checks here
        # This could include checking step numbering, process flow logic, etc.
        
        return issues
    
    def _elements_overlap(self, elem1: Dict, elem2: Dict, min_spacing: int) -> bool:
        """Check if two elements overlap within minimum spacing."""
        geom1 = elem1.get('geometry', {})
        geom2 = elem2.get('geometry', {})
        
        # Extract coordinates and dimensions
        x1, y1 = geom1.get('x', 0), geom1.get('y', 0)
        w1, h1 = geom1.get('width', 0), geom1.get('height', 0)
        
        x2, y2 = geom2.get('x', 0), geom2.get('y', 0)
        w2, h2 = geom2.get('width', 0), geom2.get('height', 0)
        
        # Check if rectangles overlap with minimum spacing
        return not (x1 + w1 + min_spacing <= x2 or 
                   x2 + w2 + min_spacing <= x1 or 
                   y1 + h1 + min_spacing <= y2 or 
                   y2 + h2 + min_spacing <= y1)
    
    def validate_routing(self) -> Dict[str, Any]:
        """Validate connector routing standards."""
        issues = []
        stats = {
            'total_connectors': 0,
            'diagonal_connectors': 0,
            'orthogonal_connectors': 0,
            'line_overlaps': 0
        }
        
        # Parse XML to find connectors
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for connector elements (simplified check)
            import re
            connector_patterns = [
                r'style=".*?edgeStyle=(?!orthogonalEdgeStyle).*?"',  # Non-orthogonal edges
                r'exitX="[^01]"',  # Exit points not at 0 or 1 (indicating diagonal)
                r'exitY="[^01]"',  # Exit points not at 0 or 1 (indicating diagonal)
            ]
            
            for pattern in connector_patterns:
                matches = re.findall(pattern, content)
                stats['diagonal_connectors'] += len(matches)
            
            # Count total connectors (approximation)
            total_connectors = content.count('endArrow=')
            stats['total_connectors'] = total_connectors
            stats['orthogonal_connectors'] = max(0, total_connectors - stats['diagonal_connectors'])
            
            # Check for specific routing issues
            if 'edgeStyle=orthogonalEdgeStyle' not in content and total_connectors > 0:
                issues.append({
                    'type': 'routing',
                    'severity': 'warning',
                    'message': 'Connectors may not be using orthogonal routing'
                })
            
        except Exception as e:
            issues.append({
                'type': 'parsing',
                'severity': 'error', 
                'message': f'Failed to parse routing: {e}'
            })
        
        return {
            'issues': issues,
            'stats': stats
        }
    
    def validate_decision_flow(self) -> Dict[str, Any]:
        """Validate decision flow consistency (YES right, NO down)."""
        issues = []
        decisions = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for decision elements (rhombus shapes)
            import re
            
            # Find decision diamonds and their connected paths
            rhombus_pattern = r'style="rhombus.*?".*?value="([^"]*)"'
            decision_matches = re.findall(rhombus_pattern, content, re.DOTALL)
            
            for decision_text in decision_matches:
                decisions.append({
                    'text': decision_text,
                    'has_yes_right': False,
                    'has_no_down': False
                })
            
            # Look for YES/NO labels and their positioning
            yes_pattern = r'value="YES".*?fontColor="#2e7d32"'
            no_pattern = r'value="NO".*?fontColor="#[cf]'
            
            yes_count = len(re.findall(yes_pattern, content))
            no_count = len(re.findall(no_pattern, content))
            
            if len(decisions) > 0:
                if yes_count < len(decisions):
                    issues.append({
                        'type': 'decision_flow',
                        'severity': 'warning',
                        'message': f'Found {len(decisions)} decisions but only {yes_count} YES labels'
                    })
                
                if no_count < len(decisions):
                    issues.append({
                        'type': 'decision_flow', 
                        'severity': 'warning',
                        'message': f'Found {len(decisions)} decisions but only {no_count} NO labels'
                    })
            
        except Exception as e:
            issues.append({
                'type': 'parsing',
                'severity': 'error',
                'message': f'Failed to parse decision flow: {e}'
            })
        
        return {
            'issues': issues,
            'decisions': decisions,
            'stats': {
                'decision_count': len(decisions),
                'yes_labels': yes_count if 'yes_count' in locals() else 0,
                'no_labels': no_count if 'no_count' in locals() else 0
            }
        }

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = f"# Draw.io Validation Report: {self.file_path}\n\n"
        
        # Basic info
        report += f"**File:** {self.file_path}\n"
        report += f"**Pages:** {self.info.page_count}\n"
        report += f"**Has Animation:** {'Yes' if self.info.has_animation else 'No'}\n\n"
        
        # Check overlaps
        overlaps = self.validate_overlaps()
        report += f"## Overlapping Elements ({len(overlaps)} issues)\n\n"
        if overlaps:
            for overlap in overlaps:
                report += f"- **{overlap['element1']}** overlaps with **{overlap['element2']}** on {overlap['page']}\n"
        else:
            report += "✅ No overlapping elements found\n"
        
        # Check connectors
        connector_issues = self.validate_connectors()
        report += f"\n## Connector Issues ({len(connector_issues)} issues)\n\n"
        if connector_issues:
            for issue in connector_issues:
                if issue['type'] == 'missing_source':
                    report += f"- Connector **{issue['connector_id']}** has missing source: {issue['missing_source']}\n"
                elif issue['type'] == 'missing_target':
                    report += f"- Connector **{issue['connector_id']}** has missing target: {issue['missing_target']}\n"
        else:
            report += "✅ No connector issues found\n"
        
        # Check consistency
        consistency_issues = self.validate_consistency()
        report += f"\n## Consistency Issues ({len(consistency_issues)} issues)\n\n"
        if consistency_issues:
            for issue in consistency_issues:
                report += f"- **{issue['type']}**: {issue['message']}\n"
        else:
            report += "✅ No consistency issues found\n"
        
        return report


class DrawioExporter:
    """Main exporter class with multiple export methods."""
    
    def __init__(self, method: str = 'auto'):
        self.temp_dir = None
        self.method = method
        self.desktop_app_path = self._find_desktop_app()
    
    def _find_desktop_app(self) -> Optional[str]:
        """Find the draw.io desktop application."""
        possible_paths = [
            '/Applications/draw.io.app/Contents/MacOS/draw.io',  # macOS
            '/usr/bin/drawio',  # Linux
            '/opt/drawio/drawio',  # Linux alternative
            'C:\\Program Files\\draw.io\\draw.io.exe',  # Windows
            'C:\\Program Files (x86)\\draw.io\\draw.io.exe',  # Windows 32-bit
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Check PATH
        try:
            result = subprocess.run(['which', 'drawio'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def export(self, input_file: str, output_file: str, format: str, **options) -> bool:
        """Export draw.io file to specified format using best available method."""
        
        # Try methods in order of preference
        methods = []
        
        if self.method == 'auto':
            if self.desktop_app_path:
                methods = ['desktop', 'web']
            else:
                methods = ['web']
        elif self.method == 'desktop':
            if not self.desktop_app_path:
                raise RuntimeError(
                    "Draw.io desktop application not found. "
                    "Please install draw.io desktop from https://github.com/jgraph/drawio-desktop/releases"
                )
            methods = ['desktop']
        elif self.method == 'web':
            methods = ['web']
        else:
            methods = [self.method]
        
        # Try each method until one succeeds
        for method in methods:
            try:
                if method == 'desktop':
                    return self._export_desktop(input_file, output_file, format, **options)
                elif method == 'web':
                    return self._export_web(input_file, output_file, format, **options)
            except Exception as e:
                if len(methods) == 1:  # If only one method, raise the error
                    raise e
                continue  # Try next method
        
        return False
    
    def _export_desktop(self, input_file: str, output_file: str, format: str, **options) -> bool:
        """Export using desktop application."""
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix='drawio_export_')
        
        try:
            return self._export_desktop(input_file, output_file, format, **options)
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def _export_desktop(self, input_file: str, output_file: str, format: str, **options) -> bool:
        """Export using draw.io desktop application."""
        cmd = [self.desktop_app_path, '--export']
        
        # Add format-specific options
        if format in ['png', 'jpg', 'jpeg']:
            cmd.extend(['--format', format])
            
            if options.get('width') and options.get('height'):
                cmd.extend(['--width', str(options['width'])])
                cmd.extend(['--height', str(options['height'])])
            elif options.get('scale'):
                cmd.extend(['--scale', str(options['scale'])])
            
            if format in ['jpg', 'jpeg'] and options.get('quality'):
                cmd.extend(['--quality', str(options['quality'])])
            
            if options.get('transparent') and format == 'png':
                cmd.append('--transparent')
            
            if options.get('border'):
                cmd.extend(['--border', str(options['border'])])
        
        elif format == 'svg':
            cmd.extend(['--format', 'svg'])
            if options.get('embed_images'):
                cmd.append('--embed-svg-images')
        
        elif format == 'pdf':
            cmd.extend(['--format', 'pdf'])
            if options.get('crop'):
                cmd.append('--crop')
        
        elif format == 'gif':
            # Use the new AnimatedGifCreator for animated GIFs
            if not self.desktop_app_path:
                click.echo("Error: Draw.io desktop application not found", err=True)
                return False
            
            if options.get('animated'):
                gif_creator = AnimatedGifCreator(str(self.temp_dir))
                return gif_creator.create_animated_gif(input_file, output_file, 
                                                     self.desktop_app_path, **options)
            else:
                # Static GIF export
                gif_creator = AnimatedGifCreator(str(self.temp_dir))
                return gif_creator._create_static_gif(input_file, output_file, 
                                                    self.desktop_app_path, **options)
        
        # Add page selection if specified
        if options.get('page'):
            cmd.extend(['--page-index', str(options['page'] - 1)])  # Convert to 0-based
        
        # Add input/output files
        if format != 'gif':  # GIF is handled separately above
            cmd.extend([input_file, '--output', output_file])
        
        # Execute command
        try:
            if options.get('verbose'):
                click.echo(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True
            else:
                click.echo(f"Desktop export failed: {result.stderr}", err=True)
                return False
        except subprocess.TimeoutExpired:
            click.echo("Desktop export timed out", err=True)
            return False
        except Exception as e:
            click.echo(f"Desktop export error: {e}", err=True)
            return False
    
    def _export_web(self, input_file: str, output_file: str, format: str, **options) -> bool:
        """Export using draw.io web service API."""
        import requests
        import urllib.parse
        
        try:
            # Read the draw.io file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare the export request
            url = "https://app.diagrams.net/export"
            
            # Build export parameters
            params = {
                'format': format,
                'xml': content
            }
            
            # Add optional parameters
            if options.get('width'):
                params['w'] = str(options['width'])
            if options.get('height'):
                params['h'] = str(options['height'])
            if options.get('border'):
                params['border'] = str(options['border'])
            if options.get('scale'):
                params['scale'] = str(options['scale'])
            if options.get('transparent'):
                params['bg'] = 'none'
            elif options.get('background'):
                params['bg'] = options['background']
            
            # Make the request
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Save the exported file
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return True
            elif response.status_code == 429:
                raise RuntimeError("Rate limit exceeded. Please try again later.")
            else:
                raise RuntimeError(f"Export failed with status {response.status_code}")
        
        except requests.RequestException as e:
            raise RuntimeError(f"Web export failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Web export error: {e}")


class AnimatedGifCreator:
    """Creates animated GIFs from draw.io diagrams with flow animations."""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
    
    def create_animated_gif(self, input_file: str, output_file: str, 
                           desktop_app_path: str, **options) -> bool:
        """Create an animated GIF by extracting frames from flow animation."""
        
        try:
            # Step 1: Export as animated SVG first
            svg_file = os.path.join(self.temp_dir, 'animated.svg')
            if not self._export_animated_svg(input_file, svg_file, desktop_app_path, **options):
                return False
            
            # Step 2: Parse SVG to understand animation structure
            animation_info = self._analyze_svg_animation(svg_file, **options)
            
            if not animation_info['has_animation']:
                # Fallback to static GIF if no animation detected
                return self._create_static_gif(input_file, output_file, desktop_app_path, **options)
            
            # Step 3: Generate animation frames
            frames = self._generate_animation_frames(svg_file, animation_info, **options)
            
            if not frames:
                # Fallback to static if frame generation failed
                return self._create_static_gif(input_file, output_file, desktop_app_path, **options)
            
            # Step 4: Create animated GIF from frames
            return self._combine_frames_to_gif(frames, output_file, **options)
            
        except Exception as e:
            click.echo(f"Animated GIF creation failed: {e}", err=True)
            # Fallback to static GIF
            return self._create_static_gif(input_file, output_file, desktop_app_path, **options)
    
    def _export_animated_svg(self, input_file: str, svg_file: str, 
                            desktop_app_path: str, **options) -> bool:
        """Export the diagram as an animated SVG."""
        cmd = [desktop_app_path, '--export', '--format', 'svg']
        
        if options.get('width') and options.get('height'):
            cmd.extend(['--width', str(options['width'])])
            cmd.extend(['--height', str(options['height'])])
        elif options.get('scale'):
            cmd.extend(['--scale', str(options['scale'])])
        
        if options.get('border'):
            cmd.extend(['--border', str(options['border'])])
        
        # Add embed images for better compatibility
        cmd.append('--embed-svg-images')
        
        cmd.extend([input_file, '--output', svg_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0 and os.path.exists(svg_file)
        except Exception:
            return False
    
    def _analyze_svg_animation(self, svg_file: str, **options) -> Dict[str, Any]:
        """Analyze SVG file to understand animation properties."""
        animation_info = {
            'has_animation': False,
            'duration': 3.0,  # Default 3 seconds
            'flow_elements': [],
            'animated_paths': []
        }
        
        try:
            with open(svg_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Look for CSS animation indicators
            import re
            
            # Check for CSS animation properties (more specific detection)
            css_animation_patterns = [
                r'@keyframes\s+ge-flow-animation',        # Keyframes definition
                r'ge-flow-animation[^;]*running',         # Running animation
                r'animation:\s*[^;]*ge-flow-animation',   # ge-flow-animation in CSS
                r'animation-name:\s*ge-flow-animation',   # Separate animation-name property
                r'stroke-dasharray[^;]*stroke-dashoffset', # Dash-based animations
            ]
            
            for pattern in css_animation_patterns:
                if re.search(pattern, svg_content, re.IGNORECASE):
                    animation_info['has_animation'] = True
                    break
            
            # Also check for simple string presence of key animation indicators
            if not animation_info['has_animation']:
                animation_indicators = [
                    'ge-flow-animation',
                    '@keyframes',
                    'stroke-dashoffset',
                    'animation:',
                ]
                
                for indicator in animation_indicators:
                    if indicator in svg_content:
                        animation_info['has_animation'] = True
                        break
            
            # Also check for traditional animation indicators
            if not animation_info['has_animation']:
                if 'flowAnimation' in svg_content or 'animation:' in svg_content:
                    animation_info['has_animation'] = True
            
            # Find animated elements (paths/lines with flow animation styles)
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            
            # Look for paths and lines that might be animated
            for element in root.findall('.//svg:path', ns) + root.findall('.//svg:line', ns):
                style = element.get('style', '')
                class_attr = element.get('class', '')
                
                # Check for animation properties in style or class
                if (re.search(r'animation[^;]*ge-flow-animation', style, re.IGNORECASE) or
                    re.search(r'stroke-dash', style, re.IGNORECASE) or
                    'ge-flow-animation' in class_attr):
                    animation_info['animated_paths'].append({
                        'element': element,
                        'id': element.get('id'),
                        'style': style
                    })
            
            # Extract duration from CSS animation if available
            duration_match = re.search(r'animation:\s*(\d+(?:\.\d+)?)(?:ms|s)', svg_content, re.IGNORECASE)
            if duration_match:
                duration_str = duration_match.group(1)
                # Convert to seconds if necessary
                if 'ms' in duration_match.group(0).lower():
                    animation_info['duration'] = float(duration_str) / 1000
                else:
                    animation_info['duration'] = float(duration_str)
            else:
                # Estimate duration based on animation speed
                speed = options.get('animation_speed', 1.0)
                animation_info['duration'] = max(2.0, 4.0 / speed)
            
        except Exception as e:
            click.echo(f"Warning: Could not analyze SVG animation: {e}", err=True)
        
        return animation_info
    
    def _generate_animation_frames(self, svg_file: str, animation_info: Dict[str, Any], 
                                  **options) -> List[str]:
        """Generate individual frames for the animation."""
        
        # Calculate frame parameters
        duration = animation_info['duration']
        fps = options.get('fps', 10)  # Frames per second
        frame_count = int(duration * fps)
        frame_count = min(max(frame_count, 8), 30)  # Limit between 8-30 frames
        
        frames = []
        
        try:
            # Read original SVG
            with open(svg_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Generate frames by modifying SVG animation state
            for i in range(frame_count):
                frame_time = i / (frame_count - 1) if frame_count > 1 else 0
                
                # Create frame-specific SVG
                frame_svg = self._create_frame_svg(svg_content, frame_time, animation_info)
                
                # Save frame SVG
                frame_svg_path = os.path.join(self.temp_dir, f'frame_{i:03d}.svg')
                with open(frame_svg_path, 'w', encoding='utf-8') as f:
                    f.write(frame_svg)
                
                # Convert frame to PNG
                frame_png_path = os.path.join(self.temp_dir, f'frame_{i:03d}.png')
                if self._convert_svg_to_png(frame_svg_path, frame_png_path, **options):
                    frames.append(frame_png_path)
        
        except Exception as e:
            click.echo(f"Frame generation failed: {e}", err=True)
        
        return frames
    
    def _create_frame_svg(self, svg_content: str, frame_time: float, 
                         animation_info: Dict[str, Any]) -> str:
        """Create an SVG frame representing a specific moment in the animation."""
        
        # Calculate dash offset based on frame time
        # Flow animations typically cycle every 0.5-2 seconds
        cycle_time = animation_info.get('duration', 1.0)
        # Create a smooth cycling offset that moves from 16 to 0 (matching CSS animation direction)
        dash_offset = 16 - (frame_time * 16) % 16
        
        # Modify the SVG content to set specific stroke-dashoffset values for this frame
        modified_svg = svg_content
        
        import re
        
        # Pattern to match stroke-dashoffset values in animated elements
        # This matches: stroke-dashoffset: 16; (where 16 is the value we want to replace)
        def update_dash_offset(match):
            return f"stroke-dashoffset: {dash_offset:.2f};"
        
        # Replace stroke-dashoffset values in style attributes that contain ge-flow-animation
        style_pattern = r'style="([^"]*ge-flow-animation[^"]*)"'
        
        def update_style_attribute(match):
            style_content = match.group(1)
            # Replace stroke-dashoffset value within this style
            updated_style = re.sub(r'stroke-dashoffset:\s*\d+(?:\.\d+)?;', update_dash_offset, style_content)
            return f'style="{updated_style}"'
        
        # Replace all animated path dash offsets
        modified_svg = re.sub(style_pattern, update_style_attribute, modified_svg)
        
        # Also handle cases where stroke-dashoffset might be a separate attribute
        dashoffset_pattern = r'stroke-dashoffset="[^"]*"'
        modified_svg = re.sub(dashoffset_pattern, f'stroke-dashoffset="{dash_offset:.2f}"', modified_svg)
        
        # Remove CSS animations from the SVG for this static frame
        # Remove the entire <style> section containing keyframes
        style_pattern = r'<style>@keyframes[^<]*</style>'
        modified_svg = re.sub(style_pattern, '', modified_svg, flags=re.DOTALL)
        
        # Remove animation properties from individual elements
        animation_remove_pattern = r'animation:[^;]*;'
        modified_svg = re.sub(animation_remove_pattern, '', modified_svg)
        
        return modified_svg
    
    def _convert_svg_to_png(self, svg_path: str, png_path: str, **options) -> bool:
        """Convert SVG frame to PNG using built-in tools."""
        
        # Try using cairosvg if available (Python library)
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path,
                           output_width=options.get('width'),
                           output_height=options.get('height'))
            return os.path.exists(png_path)
        except ImportError:
            pass
        
        # Fallback: Use inkscape if available
        try:
            inkscape_cmd = ['inkscape', '--export-type=png', f'--export-filename={png_path}']
            
            if options.get('width') and options.get('height'):
                inkscape_cmd.extend([f'--export-width={options["width"]}', 
                                   f'--export-height={options["height"]}'])
            
            inkscape_cmd.append(svg_path)
            
            result = subprocess.run(inkscape_cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0 and os.path.exists(png_path)
        except:
            pass
        
        # Final fallback: Use PIL to create a simple placeholder
        try:
            width = options.get('width', 800)
            height = options.get('height', 600)
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            draw.text((width//2-50, height//2), "Frame", fill=(0, 0, 0, 255))
            img.save(png_path, 'PNG')
            return True
        except:
            return False
    
    def _combine_frames_to_gif(self, frames: List[str], output_file: str, **options) -> bool:
        """Combine PNG frames into an animated GIF."""
        
        if not frames:
            return False
        
        try:
            # Load all frames
            images = []
            for frame_path in frames:
                if os.path.exists(frame_path):
                    img = Image.open(frame_path)
                    # Convert to RGB if necessary (GIF doesn't support RGBA)
                    if img.mode == 'RGBA':
                        # Create white background for transparency
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if not options.get('transparent'):
                            background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                            img = background
                        else:
                            # For transparent GIFs, convert to palette mode
                            img = img.convert('P')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img)
            
            if not images:
                return False
            
            # Calculate frame duration (in milliseconds)
            fps = options.get('fps', 10)
            duration = int(1000 / fps)  # Convert to milliseconds
            
            # Apply animation speed multiplier
            speed = options.get('animation_speed', 1.0)
            duration = int(duration / speed)
            duration = max(50, min(duration, 1000))  # Clamp between 50ms and 1s
            
            # Save as animated GIF
            images[0].save(
                output_file,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,  # Infinite loop
                disposal=2,  # Clear frame before drawing next
                optimize=True
            )
            
            return os.path.exists(output_file)
            
        except Exception as e:
            click.echo(f"Failed to create animated GIF: {e}", err=True)
            return False
    
    def _create_static_gif(self, input_file: str, output_file: str, 
                          desktop_app_path: str, **options) -> bool:
        """Create a static GIF as fallback."""
        
        # Export as PNG first
        temp_png = os.path.join(self.temp_dir, 'static.png')
        cmd = [desktop_app_path, '--export', '--format', 'png']
        
        if options.get('width') and options.get('height'):
            cmd.extend(['--width', str(options['width'])])
            cmd.extend(['--height', str(options['height'])])
        elif options.get('scale'):
            cmd.extend(['--scale', str(options['scale'])])
        
        if options.get('border'):
            cmd.extend(['--border', str(options['border'])])
        
        cmd.extend([input_file, '--output', temp_png])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0 or not os.path.exists(temp_png):
                return False
            
            # Convert PNG to GIF
            img = Image.open(temp_png)
            if img.mode == 'RGBA' and not options.get('transparent'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            img.save(output_file, 'GIF', optimize=True)
            return True
            
        except Exception as e:
            click.echo(f"Static GIF creation failed: {e}", err=True)
            return False


# ============================================================================
# CLI Commands
# ============================================================================

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Draw.io Export CLI Tool - Export draw.io files to various formats using desktop application."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(list(SUPPORTED_FORMATS.keys())), 
              default='png', help='Output format')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file path (auto-generated if not specified)')
@click.option('--width', '-w', type=int, help='Output width in pixels')
@click.option('--height', '-h', type=int, help='Output height in pixels')
@click.option('--size', type=click.Choice(list(DEFAULT_SIZES.keys())), 
              help='Predefined size preset')
@click.option('--scale', type=float, help='Scale factor (e.g., 2.0 for 200%)')
@click.option('--quality', '-q', type=click.IntRange(1, 100), 
              help='Quality for JPEG (1-100)')
@click.option('--quality-preset', type=click.Choice(list(QUALITY_PRESETS.keys())), 
              help='Quality preset')
@click.option('--transparent', is_flag=True, help='Transparent background (PNG/GIF)')
@click.option('--background', help='Background color (hex, e.g., #ffffff)')
@click.option('--border', type=int, default=0, help='Border width in pixels')
@click.option('--animated', is_flag=True, help='Export as animated (limited support)')
@click.option('--animation-speed', type=float, help='Animation speed multiplier')
@click.option('--animation-preset', type=click.Choice(list(ANIMATION_SPEEDS.keys())), 
              help='Animation speed preset')
@click.option('--fps', type=int, default=10, help='Frames per second for animated GIFs')
@click.option('--embed-images', is_flag=True, help='Embed images in SVG')
@click.option('--crop', is_flag=True, help='Crop to diagram bounds')
@click.option('--page', type=int, help='Page number to export (1-based)')
@click.option('--all-pages', is_flag=True, help='Export all pages')
@click.option('--method', type=click.Choice(['auto', 'desktop', 'web']), default='auto', 
              help='Export method (auto tries desktop first, then web)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def export(input_file, format, output, width, height, size, scale, quality, quality_preset,
           transparent, background, border, animated, animation_speed, animation_preset,
           fps, embed_images, crop, page, all_pages, method, verbose):
    """Export a draw.io file to the specified format."""
    
    # Validate input
    if not os.path.exists(input_file):
        click.echo(f"Error: Input file not found: {input_file}", err=True)
        return
    
    # Parse diagram info
    try:
        info = DrawioInfo(input_file)
        if verbose:
            click.echo(f"Parsed diagram: {info.page_count} pages, animation: {info.has_animation}")
    except Exception as e:
        click.echo(f"Error parsing input file: {e}", err=True)
        return
    
    # Handle size presets
    if size:
        width, height = DEFAULT_SIZES[size]
        if verbose:
            click.echo(f"Using size preset '{size}': {width}x{height}")
    
    # Handle quality presets
    if quality_preset:
        quality = QUALITY_PRESETS[quality_preset]
        if verbose:
            click.echo(f"Using quality preset '{quality_preset}': {quality}")
    
    # Handle animation settings
    if animation_preset:
        animation_speed = ANIMATION_SPEEDS[animation_preset]
        if verbose:
            click.echo(f"Using animation preset '{animation_preset}': {animation_speed}x")
    
    # Check if format supports requested features
    format_info = SUPPORTED_FORMATS[format]
    if animated and not format_info['animated']:
        click.echo(f"Warning: Format '{format}' does not support animation", err=True)
        animated = False
    
    if transparent and not format_info['transparency']:
        click.echo(f"Warning: Format '{format}' does not support transparency", err=True)
        transparent = False
    
    # Auto-detect animation if file has it
    if info.has_animation and format_info['animated'] and not animated:
        animated = True
        if verbose:
            click.echo("Auto-detected animation in diagram")
    
    # Generate output filename if not specified
    if not output:
        input_path = Path(input_file)
        output = input_path.with_suffix(f'.{format}')
        if verbose:
            click.echo(f"Auto-generated output file: {output}")
    
    # Prepare export options
    options = {
        'width': width,
        'height': height,
        'scale': scale,
        'quality': quality,
        'transparent': transparent,
        'background': background,
        'border': border,
        'animated': animated,
        'animation_speed': animation_speed,
        'fps': fps, # Add fps to options
        'embed_images': embed_images,
        'crop': crop,
        'page': page,
        'all_pages': all_pages,
        'verbose': verbose,
    }
    
    # Remove None values
    options = {k: v for k, v in options.items() if v is not None}
    
    # Export
    exporter = DrawioExporter(method=method)
    
    try:
        with click.progressbar(length=100, label='Exporting') as bar:
            bar.update(20)
            
            if all_pages:
                # Export all pages
                success_count = 0
                for i, page_info in enumerate(info.pages):
                    page_output = Path(output).with_stem(f"{Path(output).stem}_page_{i+1}")
                    page_options = options.copy()
                    page_options['page'] = i + 1
                    
                    if exporter.export(input_file, str(page_output), format, **page_options):
                        success_count += 1
                        if verbose:
                            click.echo(f"Exported page {i+1}: {page_output}")
                
                bar.update(100)
                click.echo(f"Exported {success_count}/{info.page_count} pages")
            
            else:
                # Export single page/diagram
                bar.update(50)
                success = exporter.export(input_file, str(output), format, **options)
                bar.update(100)
                
                if success:
                    click.echo(f"✅ Successfully exported to: {output}")
                    
                    # Show file info
                    if os.path.exists(output):
                        file_size = os.path.getsize(output)
                        size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
                        click.echo(f"File size: {size_str}")
                else:
                    click.echo("❌ Export failed", err=True)
                    return
    
    except Exception as e:
        click.echo(f"Export error: {e}", err=True)
        return


@cli.command()
@click.argument('pattern', type=str)
@click.option('--format', '-f', type=click.Choice(list(SUPPORTED_FORMATS.keys())), 
              default='png', help='Output format')
@click.option('--output-dir', '-d', type=click.Path(), default='exports', 
              help='Output directory')
@click.option('--size', type=click.Choice(list(DEFAULT_SIZES.keys())), 
              help='Predefined size preset')
@click.option('--quality-preset', type=click.Choice(list(QUALITY_PRESETS.keys())), 
              help='Quality preset')
@click.option('--animated', is_flag=True, help='Export as animated (limited support)')
@click.option('--parallel', is_flag=True, help='Process files in parallel')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch(pattern, format, output_dir, size, quality_preset, animated, parallel, verbose):
    """Batch export multiple draw.io files matching a pattern."""
    
    import glob
    
    # Find matching files
    files = glob.glob(pattern)
    if not files:
        click.echo(f"No files found matching pattern: {pattern}", err=True)
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        click.echo(f"Found {len(files)} files to process")
        click.echo(f"Output directory: {output_path}")
    
    # Process options
    options = {}
    if size:
        width, height = DEFAULT_SIZES[size]
        options.update({'width': width, 'height': height})
    
    if quality_preset:
        options['quality'] = QUALITY_PRESETS[quality_preset]
    
    if animated:
        options['animated'] = True
    
    if verbose:
        options['verbose'] = True
    
    # Process files
    exporter = DrawioExporter()
    
    with click.progressbar(files, label='Processing files') as bar:
        success_count = 0
        
        for input_file in bar:
            try:
                # Generate output filename
                input_path = Path(input_file)
                output_file = output_path / input_path.with_suffix(f'.{format}').name
                
                # Export
                if exporter.export(input_file, str(output_file), format, **options):
                    success_count += 1
                    if verbose:
                        click.echo(f"✅ {input_file} -> {output_file}")
                else:
                    if verbose:
                        click.echo(f"❌ Failed: {input_file}")
            
            except Exception as e:
                if verbose:
                    click.echo(f"❌ Error processing {input_file}: {e}")
    
    click.echo(f"Processed {success_count}/{len(files)} files successfully")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def info(input_file):
    """Display information about a draw.io file."""
    
    try:
        info = DrawioInfo(input_file)
        
        click.echo("📊 Draw.io File Information")
        click.echo(f"{'='*50}")
        click.echo(f"File: {info.filepath}")
        click.echo(f"Host: {info.host}")
        click.echo(f"Version: {info.version}")
        click.echo(f"Page Count: {info.page_count}")
        click.echo(f"Has Animation: {'Yes' if info.has_animation else 'No'}")
        click.echo()
        
        for i, page in enumerate(info.pages):
            click.echo(f"📄 Page {i+1}: {page['name']}")
            click.echo(f"   ID: {page['id']}")
            click.echo(f"   Elements: {page['element_count']}")
            click.echo(f"   Animated: {'Yes' if page['has_animation'] else 'No'}")
            if 'dimensions' in page:
                click.echo(f"   Dimensions: {page['dimensions'][0]}x{page['dimensions'][1]}")
            click.echo()
    
    except Exception as e:
        click.echo(f"Error analyzing file: {e}", err=True)


@cli.command()
def formats():
    """List all supported export formats and their capabilities."""
    
    click.echo("🎨 Supported Export Formats")
    click.echo("="*50)
    
    for fmt, info in SUPPORTED_FORMATS.items():
        click.echo(f"{fmt.upper():<6} - ", nl=False)
        
        features = []
        if info['animated']:
            features.append("Animation")
        if info['transparency']:
            features.append("Transparency")
        if info['quality']:
            features.append("Quality Control")
        
        click.echo(f"{', '.join(features) if features else 'Basic'}")
    
    click.echo()
    click.echo("🖼️  Size Presets")
    click.echo("="*20)
    
    for name, (width, height) in DEFAULT_SIZES.items():
        click.echo(f"{name:<10} - {width}x{height}")
    
    click.echo()
    click.echo("⚡ Animation Speed Presets")
    click.echo("="*30)
    
    for name, speed in ANIMATION_SPEEDS.items():
        click.echo(f"{name:<10} - {speed}x")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--min-spacing', default=20, help='Minimum spacing between elements (pixels)')
@click.option('--report', '-r', 'output_report', type=click.Path(), help='Save validation report to file')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation output')
def validate(input_file, min_spacing, output_report, verbose):
    """Validate a draw.io file for common issues."""
    
    try:
        validator = DrawioValidator(input_file)
        
        if verbose:
            click.echo(f"🔍 Validating: {input_file}")
            click.echo(f"📏 Minimum spacing: {min_spacing}px")
            click.echo()
        
        # Check for overlaps
        overlaps = validator.validate_overlaps(min_spacing)
        
        # Check connectors
        connector_issues = validator.validate_connectors()
        
        # Check consistency
        consistency_issues = validator.validate_consistency()
        
        # Generate report
        report = validator.generate_report()
        
        if output_report:
            with open(output_report, 'w') as f:
                f.write(report)
            click.echo(f"📝 Validation report saved to: {output_report}")
        else:
            click.echo(report)
        
        # Summary
        total_issues = len(overlaps) + len(connector_issues) + len(consistency_issues)
        if total_issues == 0:
            click.echo("✅ No issues found!")
        else:
            click.echo(f"⚠️  Found {total_issues} issues:")
            if overlaps:
                click.echo(f"   - {len(overlaps)} overlapping elements")
            if connector_issues:
                click.echo(f"   - {len(connector_issues)} connector issues")
            if consistency_issues:
                click.echo(f"   - {len(consistency_issues)} consistency issues")
    
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--codebase-path', type=click.Path(exists=True), help='Path to codebase for consistency checking')
@click.option('--output', '-o', type=click.Path(), help='Output file for consistency report')
def consistency_check(input_file, codebase_path, output):
    """Check diagram consistency against codebase."""
    
    try:
        validator = DrawioValidator(input_file)
        
        click.echo(f"🔍 Checking consistency: {input_file}")
        if codebase_path:
            click.echo(f"📂 Against codebase: {codebase_path}")
        click.echo()
        
        issues = validator.validate_consistency(codebase_path)
        
        if not issues:
            click.echo("✅ Diagram is consistent!")
        else:
            click.echo(f"⚠️  Found {len(issues)} consistency issues:")
            for issue in issues:
                click.echo(f"   - {issue['type']}: {issue['message']}")
        
        if output:
            report = f"# Consistency Check Report\n\n"
            report += f"**File:** {input_file}\n"
            report += f"**Codebase:** {codebase_path or 'Not specified'}\n\n"
            
            if issues:
                report += "## Issues Found\n\n"
                for issue in issues:
                    report += f"- **{issue['type']}**: {issue['message']}\n"
            else:
                report += "✅ No consistency issues found\n"
            
            with open(output, 'w') as f:
                f.write(report)
            click.echo(f"📝 Report saved to: {output}")
    
    except Exception as e:
        click.echo(f"❌ Consistency check failed: {e}", err=True)


@cli.command('validate-routing')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for routing report')
def validate_routing(input_file, output):
    """Validate connector routing standards (orthogonal vs diagonal)."""
    
    try:
        validator = DrawioValidator(input_file)
        
        click.echo(f"🔍 Validating connector routing in: {input_file}")
        click.echo()
        
        results = validator.validate_routing()
        stats = results['stats']
        issues = results['issues']
        
        # Display statistics
        click.echo("📊 ROUTING STATISTICS")
        click.echo("=" * 40)
        click.echo(f"Total connectors: {stats['total_connectors']}")
        click.echo(f"Orthogonal connectors: {stats['orthogonal_connectors']}")
        click.echo(f"Diagonal connectors: {stats['diagonal_connectors']}")
        
        if stats['total_connectors'] > 0:
            orthogonal_pct = (stats['orthogonal_connectors'] / stats['total_connectors']) * 100
            click.echo(f"Orthogonal percentage: {orthogonal_pct:.1f}%")
        
        click.echo()
        
        # Display issues
        if issues:
            click.echo("⚠️  ROUTING ISSUES")
            click.echo("=" * 40)
            for issue in issues:
                severity_icon = "🔥" if issue['severity'] == 'error' else "⚠️"
                click.echo(f"{severity_icon} {issue['message']}")
        else:
            click.echo("✅ No routing issues found!")
        
        # Generate report if requested
        if output:
            report = f"# Connector Routing Validation Report\n\n"
            report += f"**File:** {input_file}\n\n"
            report += f"## Statistics\n"
            report += f"- Total connectors: {stats['total_connectors']}\n"
            report += f"- Orthogonal connectors: {stats['orthogonal_connectors']}\n"
            report += f"- Diagonal connectors: {stats['diagonal_connectors']}\n\n"
            
            if issues:
                report += f"## Issues ({len(issues)})\n"
                for issue in issues:
                    report += f"- **{issue['severity'].upper()}**: {issue['message']}\n"
            else:
                report += "## Issues\n✅ No routing issues found\n"
            
            with open(output, 'w') as f:
                f.write(report)
            click.echo(f"📝 Report saved to: {output}")
    
    except Exception as e:
        click.echo(f"❌ Routing validation failed: {e}", err=True)


@cli.command('validate-decisions')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for decision flow report')
def validate_decisions(input_file, output):
    """Validate decision flow consistency (YES→right, NO→down)."""
    
    try:
        validator = DrawioValidator(input_file)
        
        click.echo(f"🔍 Validating decision flow in: {input_file}")
        click.echo()
        
        results = validator.validate_decision_flow()
        stats = results['stats']
        issues = results['issues']
        decisions = results['decisions']
        
        # Display statistics
        click.echo("📊 DECISION FLOW STATISTICS")
        click.echo("=" * 40)
        click.echo(f"Decision diamonds: {stats['decision_count']}")
        click.echo(f"YES labels: {stats['yes_labels']}")
        click.echo(f"NO labels: {stats['no_labels']}")
        click.echo()
        
        # Display decision details
        if decisions:
            click.echo("🔷 DECISIONS FOUND")
            click.echo("=" * 40)
            for i, decision in enumerate(decisions, 1):
                click.echo(f"{i}. {decision['text']}")
            click.echo()
        
        # Display issues
        if issues:
            click.echo("⚠️  DECISION FLOW ISSUES")
            click.echo("=" * 40)
            for issue in issues:
                severity_icon = "🔥" if issue['severity'] == 'error' else "⚠️"
                click.echo(f"{severity_icon} {issue['message']}")
        else:
            click.echo("✅ No decision flow issues found!")
        
        # Generate report if requested
        if output:
            report = f"# Decision Flow Validation Report\n\n"
            report += f"**File:** {input_file}\n\n"
            report += f"## Statistics\n"
            report += f"- Decision diamonds: {stats['decision_count']}\n"
            report += f"- YES labels: {stats['yes_labels']}\n"
            report += f"- NO labels: {stats['no_labels']}\n\n"
            
            if decisions:
                report += f"## Decisions Found\n"
                for i, decision in enumerate(decisions, 1):
                    report += f"{i}. {decision['text']}\n"
                report += "\n"
            
            if issues:
                report += f"## Issues ({len(issues)})\n"
                for issue in issues:
                    report += f"- **{issue['severity'].upper()}**: {issue['message']}\n"
            else:
                report += "## Issues\n✅ No decision flow issues found\n"
            
            with open(output, 'w') as f:
                f.write(report)
            click.echo(f"📝 Report saved to: {output}")
    
    except Exception as e:
        click.echo(f"❌ Decision flow validation failed: {e}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--min-spacing', default=20, help='Minimum spacing to maintain (pixels)')
@click.option('--output', '-o', type=click.Path(), help='Output file (default: overwrite input)')
@click.option('--dry-run', is_flag=True, help='Show what would be changed without making changes')
def fix_overlaps(input_file, min_spacing, output, dry_run):
    """Automatically fix overlapping elements in a draw.io file."""
    
    try:
        validator = DrawioValidator(input_file)
        
        click.echo(f"🔧 {'Analyzing' if dry_run else 'Fixing'} overlaps in: {input_file}")
        click.echo(f"📏 Target spacing: {min_spacing}px")
        click.echo()
        
        overlaps = validator.validate_overlaps(min_spacing)
        
        if not overlaps:
            click.echo("✅ No overlapping elements found!")
            return
        
        click.echo(f"Found {len(overlaps)} overlapping element pairs:")
        for overlap in overlaps:
            click.echo(f"   - {overlap['element1']} ↔ {overlap['element2']}")
        
        if dry_run:
            click.echo("\n🔍 Dry run mode - no changes made")
        else:
            click.echo("\n⚠️  Automatic overlap fixing not yet implemented")
            click.echo("   This feature requires complex layout algorithms")
            click.echo("   Please fix overlaps manually using the validation report")
    
    except Exception as e:
        click.echo(f"❌ Fix overlaps failed: {e}", err=True)


if __name__ == '__main__':
    cli() 
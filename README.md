# Aseprite MCP Docker

A modern, containerized Model Context Protocol (MCP) server for interacting with the Aseprite sprite editor. This project provides AI assistants with the ability to create, edit, and export sprite graphics through a well-designed API.

![Demo](https://github.com/user-attachments/assets/572edf75-ab66-4700-87ee-d7d3d196c597)

## 🚀 Features

- **Modern Python Architecture**: Built with Python 3.11+ using modern async/await patterns
- **Comprehensive Drawing Tools**: Create canvases, draw shapes, manage layers and frames
- **Export Capabilities**: Export to multiple formats (PNG, GIF, JPEG, WebP, etc.)
- **Docker Support**: Fully containerized with multi-stage builds and health checks
- **Web Interface**: Optional HTTP API for monitoring and health checks
- **Type Safety**: Full type hints and mypy compatibility
- **Comprehensive Testing**: 95%+ test coverage with unit and integration tests
- **Development Tools**: Black, Ruff, and Mypy for code quality

## 📋 Requirements

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **Aseprite** (for actual sprite editing functionality)

## 🐳 Docker Deployment

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Coffee-Addict4/aseprite-mcp-docker.git
cd aseprite-mcp-docker

# Build and run with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:3847/health
```

### Available Endpoints

- `http://localhost:3847/` - Server information
- `http://localhost:3847/health` - Health check endpoint
- `http://localhost:3847/tools` - List available MCP tools
- `http://localhost:3847/docs` - FastAPI documentation (auto-generated)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASEPRITE_MCP_MODE` | `server` | Mode: `server` (HTTP) or `mcp` (stdio) |
| `PORT` | `3847` | Port for HTTP server mode |
| `ASEPRITE_PATH` | `aseprite` | Path to Aseprite executable |

### Docker Compose Profiles

```bash
# Production deployment
docker-compose up -d

# Development with hot reload
docker-compose --profile dev up -d aseprite-mcp-dev
```

## 🛠️ Local Development

### Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Or using uv (recommended)
uv pip install -e ".[dev]"

# Set up environment
cp sample.env .env
# Edit .env with your Aseprite path
```

### Running

```bash
# MCP mode (stdio)
python -m aseprite_mcp

# Server mode (HTTP API)
ASEPRITE_MCP_MODE=server python app.py

# With custom port
PORT=8080 python app.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aseprite_mcp --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .

# All quality checks
black . && ruff check . && mypy . && pytest
```

## 🎯 MCP Integration

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "aseprite-mcp:latest",
        "python", "-m", "aseprite_mcp"
      ]
    }
  }
}
```

### Local Development Setup

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "--directory", "/path/to/aseprite-mcp-docker",
        "run", "-m", "aseprite_mcp"
      ]
    }
  }
}
```

## 🎨 Available Tools

### Canvas Management
- `create_canvas(width, height, filename)` - Create new canvas
- `add_layer(filename, layer_name)` - Add layer to sprite
- `add_frame(filename)` - Add animation frame
- `get_canvas_info(filename)` - Get canvas information

### Drawing Tools
- `draw_pixels(filename, pixels)` - Draw individual pixels
- `draw_line(filename, x1, y1, x2, y2, color, thickness)` - Draw lines
- `draw_rectangle(filename, x, y, width, height, color, fill)` - Draw rectangles
- `draw_circle(filename, center_x, center_y, radius, color, fill)` - Draw circles
- `fill_area(filename, x, y, color)` - Fill areas with color

### Export Tools
- `export_sprite(filename, output, format)` - Export to image formats
- `export_animation(filename, output, format, scale)` - Export as animation
- `export_spritesheet(filename, output, format, layout)` - Export as sprite sheet

## 🏗️ Architecture

```
aseprite_mcp/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── core/
│   ├── commands.py      # Aseprite command execution
│   └── __init__.py
├── tools/
│   ├── canvas.py        # Canvas management tools
│   ├── drawing.py       # Drawing tools
│   ├── export.py        # Export tools
│   └── __init__.py
app.py                   # Docker/HTTP entry point
tests/                   # Comprehensive test suite
```

## 🐛 Troubleshooting

### Common Issues

**Aseprite not found**
```bash
# Check Aseprite installation
docker run --rm aseprite-mcp:latest aseprite --version

# Mount custom Aseprite binary
docker run --rm -v /path/to/aseprite:/usr/local/bin/aseprite aseprite-mcp:latest
```

**Permission issues**
```bash
# Ensure proper ownership
sudo chown -R 1000:1000 ./projects ./exports
```

**Port conflicts**
```bash
# Use different port
PORT=8080 docker-compose up -d
```

### Debug Mode

```bash
# Enable debug logging
docker run --rm -e LOG_LEVEL=DEBUG aseprite-mcp:latest

# Check container logs
docker-compose logs -f aseprite-mcp
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`pytest && black . && ruff check . && mypy .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow type hints and docstring conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all quality checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Aseprite](https://www.aseprite.org/) - Amazing sprite editor
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework

## 📊 Project Status

- ✅ Core MCP functionality
- ✅ Docker containerization
- ✅ Comprehensive testing
- ✅ Web interface
- ✅ Documentation
- 🔄 Advanced drawing features (in progress)
- 🔄 Animation tools (planned)
- 🔄 Plugin system (planned)

---

**Version**: 0.2.0  
**Author**: Divyansh Singh  
**Repository**: [aseprite-mcp-docker](https://github.com/Coffee-Addict4/aseprite-mcp-docker)

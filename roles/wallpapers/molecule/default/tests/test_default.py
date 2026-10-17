BACKGROUNDS = "/root/.local/share/backgrounds"


def test_svg_has_the_colors_of_the_theme(host):
    """The SVG is generated from the role file with the colors substituted."""
    svg = host.file(f"{BACKGROUNDS}/coding.svg")
    assert svg.is_file
    content = svg.content_string
    assert "$OUTLINE" not in content
    assert "#f2cdcd" in content
    assert "#1e1e2e" in content


def test_png_is_generated(host):
    """ImageMagick converts the SVG to a PNG image."""
    png = host.file(f"{BACKGROUNDS}/coding.png")
    assert png.is_file
    assert host.check_output(f"head -c 8 {png.path} | od -An -tx1").split() == "89 50 4e 47 0d 0a 1a 0a".split()
    assert png.size > 1000


def test_links(host):
    """wallpaper and locker point to the generated images."""
    for name in ("wallpaper", "locker"):
        for extension in ("svg", "png"):
            link = host.file(f"{BACKGROUNDS}/{name}.{extension}")
            assert link.is_symlink, link.path
            assert link.linked_to == f"{BACKGROUNDS}/coding.{extension}"

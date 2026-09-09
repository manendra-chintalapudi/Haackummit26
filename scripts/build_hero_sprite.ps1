param(
  [string]$InputVideo = "frontend/assets/synapse-interactive-hero.mp4",
  [string]$OutputSprite = "frontend/assets/synapse-hero-sprite.webp"
)

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) { throw "ffmpeg is required. Install it and add it to PATH." }

# 120 frames at 12 fps keeps the sheet below browser image-size limits.
& $ffmpeg.Source -y -i $InputVideo `
  -vf "fps=12,scale=128:72:flags=lanczos,tile=120x1:padding=0:margin=0" `
  -frames:v 1 -c:v libwebp -q:v 80 $OutputSprite

if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed with exit code $LASTEXITCODE" }

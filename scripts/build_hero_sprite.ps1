param(
  [string]$InputVideo = "frontend/assets/synapse-interactive-hero.mp4",
  [string]$OutputSprite = "frontend/assets/synapse-hero-sprite.png"
)

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) { throw "ffmpeg is required. Install it and add it to PATH." }

# The source is 24 fps for 10 seconds: 240 frames total.
& $ffmpeg.Source -y -i $InputVideo `
  -vf "scale=120:68:flags=lanczos,tile=240x1:padding=0:margin=0" `
  -frames:v 1 -c:v png $OutputSprite

if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed with exit code $LASTEXITCODE" }

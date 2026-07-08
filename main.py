from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import zipfile
from sprite_generator import SpriteGenerator
from sound_generator import SoundGenerator

app = FastAPI(
    title="Procedural Asset Generation API",
    description="Generate retro-style pixel art sprites and sound effects procedurally",
    version="1.1.0"
)

sprite_gen = SpriteGenerator()
sound_gen = SoundGenerator()

class SpriteRequest(BaseModel):
    type: str
    seed: Optional[int] = None
    size: Optional[int] = None
    style: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None

class SoundRequest(BaseModel):
    type: str
    seed: Optional[int] = None
    duration: Optional[float] = None

class BatchSpriteRequest(BaseModel):
    types: List[str]
    seed: Optional[int] = None
    size: Optional[int] = None
    style: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None

class BatchSoundRequest(BaseModel):
    types: List[str]
    seed: Optional[int] = None

@app.get("/")
def read_root():
    return {
        "message": "Procedural Asset Generation API",
        "version": "1.1.0",
        "endpoints": {
            "sprites": "/generate/sprite",
            "sprites_batch": "/generate/sprites/batch",
            "sounds": "/generate/sound",
            "sounds_batch": "/generate/sounds/batch",
            "sprite_types": "/sprites/types",
            "sound_types": "/sounds/types",
            "style_presets": "/styles/presets"
        }
    }

def parse_color(color_str: Optional[str]) -> Optional[tuple]:
    """Parse hex color string to RGB tuple"""
    if not color_str:
        return None
    color_str = color_str.lstrip('#')
    if len(color_str) == 6:
        return tuple(int(color_str[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return None

def get_style_colors(style: str) -> Optional[dict]:
    """Get color palette for a style preset"""
    styles = {
        "retro": {
            "primary": "#FF6B35",
            "secondary": "#F7931E", 
            "accent": "#FFD23F"
        },
        "neon": {
            "primary": "#FF006E",
            "secondary": "#8338EC",
            "accent": "#3A86FF"
        },
        "monochrome": {
            "primary": "#FFFFFF",
            "secondary": "#888888",
            "accent": "#444444"
        },
        "cyberpunk": {
            "primary": "#00F0FF",
            "secondary": "#FF003C",
            "accent": "#FFD700"
        },
        "forest": {
            "primary": "#2D5016",
            "secondary": "#5A8C3C",
            "accent": "#A4C639"
        },
        "ocean": {
            "primary": "#006994",
            "secondary": "#00A8CC",
            "accent": "#7FD8BE"
        },
        "sunset": {
            "primary": "#FF6B6B",
            "secondary": "#FFA07A",
            "accent": "#FFE66D"
        }
    }
    return styles.get(style.lower())

@app.get("/styles/presets")
def get_style_presets():
    """List available style presets"""
    return {
        "presets": {
            "retro": {
                "description": "Classic 80s arcade colors",
                "colors": get_style_colors("retro")
            },
            "neon": {
                "description": "Vibrant neon colors",
                "colors": get_style_colors("neon")
            },
            "monochrome": {
                "description": "Black and white grayscale",
                "colors": get_style_colors("monochrome")
            },
            "cyberpunk": {
                "description": "High-tech cyberpunk aesthetic",
                "colors": get_style_colors("cyberpunk")
            },
            "forest": {
                "description": "Natural green tones",
                "colors": get_style_colors("forest")
            },
            "ocean": {
                "description": "Deep sea blues and teals",
                "colors": get_style_colors("ocean")
            },
            "sunset": {
                "description": "Warm sunset colors",
                "colors": get_style_colors("sunset")
            }
        }
    }

@app.post("/generate/sprite")
def generate_sprite(request: SpriteRequest):
    try:
        sprite_map = {
            "player": sprite_gen.generate_player_ship,
            "enemy_grunt": sprite_gen.generate_enemy_grunt,
            "enemy_drone": sprite_gen.generate_enemy_drone,
            "enemy_turret": sprite_gen.generate_enemy_turret,
            "enemy_carrier": sprite_gen.generate_enemy_carrier,
            "enemy_flanker": sprite_gen.generate_enemy_flanker,
            "enemy_kamikaze": sprite_gen.generate_enemy_kamikaze,
            "enemy_bomber": sprite_gen.generate_enemy_bomber,
            "enemy_weaver": sprite_gen.generate_enemy_weaver,
            "boss_core": sprite_gen.generate_boss_core,
            "boss_gun": sprite_gen.generate_boss_gun,
            "vulcan_bullet": sprite_gen.generate_vulcan_bullet,
            "laser_bolt": sprite_gen.generate_laser_bolt,
            "spread_bullet": sprite_gen.generate_spread_bullet,
            "missile": sprite_gen.generate_missile,
            "enemy_bullet": sprite_gen.generate_enemy_bullet,
            "power_up": sprite_gen.generate_power_up,
            "bomb": sprite_gen.generate_bomb,
            "explosion_sheet": sprite_gen.generate_explosion_sheet,
            "spark_sheet": sprite_gen.generate_spark_sheet,
            "background_stars": sprite_gen.generate_background_stars,
        }
        
        if request.type not in sprite_map:
            raise HTTPException(status_code=400, detail=f"Unknown sprite type: {request.type}")
        
        # Apply style preset if specified
        if request.style:
            style_colors = get_style_colors(request.style)
            if style_colors:
                request.primary_color = request.primary_color or style_colors["primary"]
                request.secondary_color = request.secondary_color or style_colors["secondary"]
                request.accent_color = request.accent_color or style_colors["accent"]
        
        # Generate sprite
        img = sprite_map[request.type](request.seed)
        
        # Apply color customization if provided
        if request.primary_color or request.secondary_color or request.accent_color:
            img = sprite_gen.apply_color_tint(
                img,
                primary_color=parse_color(request.primary_color),
                secondary_color=parse_color(request.secondary_color),
                accent_color=parse_color(request.accent_color)
            )
        
        if request.size and request.size != img.width:
            aspect = img.height / img.width
            new_height = int(request.size * aspect)
            img = img.resize((request.size, new_height), resample=0)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return StreamingResponse(img_bytes, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/sprites/batch")
def generate_sprites_batch(request: BatchSpriteRequest):
    try:
        sprite_map = {
            "player": sprite_gen.generate_player_ship,
            "enemy_grunt": sprite_gen.generate_enemy_grunt,
            "enemy_drone": sprite_gen.generate_enemy_drone,
            "enemy_turret": sprite_gen.generate_enemy_turret,
            "enemy_carrier": sprite_gen.generate_enemy_carrier,
            "enemy_flanker": sprite_gen.generate_enemy_flanker,
            "enemy_kamikaze": sprite_gen.generate_enemy_kamikaze,
            "enemy_bomber": sprite_gen.generate_enemy_bomber,
            "enemy_weaver": sprite_gen.generate_enemy_weaver,
            "boss_core": sprite_gen.generate_boss_core,
            "boss_gun": sprite_gen.generate_boss_gun,
            "vulcan_bullet": sprite_gen.generate_vulcan_bullet,
            "laser_bolt": sprite_gen.generate_laser_bolt,
            "spread_bullet": sprite_gen.generate_spread_bullet,
            "missile": sprite_gen.generate_missile,
            "enemy_bullet": sprite_gen.generate_enemy_bullet,
            "power_up": sprite_gen.generate_power_up,
            "bomb": sprite_gen.generate_bomb,
            "explosion_sheet": sprite_gen.generate_explosion_sheet,
            "spark_sheet": sprite_gen.generate_spark_sheet,
            "background_stars": sprite_gen.generate_background_stars,
        }
        
        # Validate all types
        for sprite_type in request.types:
            if sprite_type not in sprite_map:
                raise HTTPException(status_code=400, detail=f"Unknown sprite type: {sprite_type}")
        
        # Apply style preset if specified
        if request.style:
            style_colors = get_style_colors(request.style)
            if style_colors:
                request.primary_color = request.primary_color or style_colors["primary"]
                request.secondary_color = request.secondary_color or style_colors["secondary"]
                request.accent_color = request.accent_color or style_colors["accent"]
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for sprite_type in request.types:
                # Generate sprite
                img = sprite_map[sprite_type](request.seed)
                
                # Apply color customization if provided
                if request.primary_color or request.secondary_color or request.accent_color:
                    img = sprite_gen.apply_color_tint(
                        img,
                        primary_color=parse_color(request.primary_color),
                        secondary_color=parse_color(request.secondary_color),
                        accent_color=parse_color(request.accent_color)
                    )
                
                if request.size and request.size != img.width:
                    aspect = img.height / img.width
                    new_height = int(request.size * aspect)
                    img = img.resize((request.size, new_height), resample=0)
                
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                zip_file.writestr(f"{sprite_type}.png", img_bytes.getvalue())
        
        zip_buffer.seek(0)
        return StreamingResponse(zip_buffer, media_type="application/zip")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/sounds/batch")
def generate_sounds_batch(request: BatchSoundRequest):
    try:
        sound_map = {
            "vulcan": sound_gen.generate_vulcan_sound,
            "laser": sound_gen.generate_laser_sound,
            "spread": sound_gen.generate_spread_sound,
            "missile": sound_gen.generate_missile_sound,
            "explosion_small": sound_gen.generate_explosion_small,
            "explosion_medium": sound_gen.generate_explosion_medium,
            "explosion_large": sound_gen.generate_explosion_large,
            "player_death": sound_gen.generate_player_death,
            "ui_click": sound_gen.generate_ui_click,
            "ui_hover": sound_gen.generate_ui_hover,
            "ui_confirm": sound_gen.generate_ui_confirm,
            "ui_cancel": sound_gen.generate_ui_cancel,
            "powerup": sound_gen.generate_powerup_sound,
        }
        
        # Validate all types
        for sound_type in request.types:
            if sound_type not in sound_map:
                raise HTTPException(status_code=400, detail=f"Unknown sound type: {sound_type}")
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for sound_type in request.types:
                wav_bytes = sound_map[sound_type](request.seed)
                zip_file.writestr(f"{sound_type}.wav", wav_bytes)
        
        zip_buffer.seek(0)
        return StreamingResponse(zip_buffer, media_type="application/zip")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/sound")
def generate_sound(request: SoundRequest):
    try:
        if request.type == "vulcan":
            wav_bytes = sound_gen.generate_vulcan_sound(request.seed)
        elif request.type == "laser":
            wav_bytes = sound_gen.generate_laser_sound(request.seed)
        elif request.type == "spread":
            wav_bytes = sound_gen.generate_spread_sound(request.seed)
        elif request.type == "missile":
            wav_bytes = sound_gen.generate_missile_sound(request.seed)
        elif request.type == "explosion_small":
            wav_bytes = sound_gen.generate_explosion_small(request.seed)
        elif request.type == "explosion_medium":
            wav_bytes = sound_gen.generate_explosion_medium(request.seed)
        elif request.type == "explosion_large":
            wav_bytes = sound_gen.generate_explosion_large(request.seed)
        elif request.type == "player_death":
            wav_bytes = sound_gen.generate_player_death(request.seed)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown sound type: {request.type}")
        
        return Response(content=wav_bytes, media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sprites/types")
def get_sprite_types():
    return {
        "types": {
            "ships": ["player"],
            "enemies": ["enemy_grunt", "enemy_drone", "enemy_turret", "enemy_carrier", 
                       "enemy_flanker", "enemy_kamikaze", "enemy_bomber", "enemy_weaver"],
            "bosses": ["boss_core", "boss_gun"],
            "projectiles": ["vulcan_bullet", "laser_bolt", "spread_bullet", "missile", "enemy_bullet"],
            "items": ["power_up", "bomb"],
            "effects": ["explosion_sheet", "spark_sheet"],
            "backgrounds": ["background_stars"]
        },
        "description": "Available sprite types for generation",
        "total": 21,
        "customization": {
            "style_presets": ["retro", "neon", "monochrome", "cyberpunk", "forest", "ocean", "sunset"],
            "custom_colors": "Use primary_color, secondary_color, accent_color (hex format: #RRGGBB)"
        }
    }

@app.get("/sounds/types")
def get_sound_types():
    return {
        "types": {
            "weapons": ["vulcan", "laser", "spread", "missile"],
            "explosions": ["explosion_small", "explosion_medium", "explosion_large"],
            "player": ["player_death"],
            "ui": ["ui_click", "ui_hover", "ui_confirm", "ui_cancel"],
            "items": ["powerup"]
        },
        "description": "Available sound types for generation",
        "total": 13
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

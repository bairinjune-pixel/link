import json
import logging
import re
from aiohttp import web
from web.bot import multi_clients, work_loads
from web.server.exceptions import FileNotFound, InvalidHash
from web.utils.custom_dl import ByteStreamer
from web.utils.render_template import render_mini_app
from info import *
from utils import temp, get_readable_time
from web.utils.file_properties import get_hash
from database.users_db import db

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

class_cache = {}

# Mini App - Main Page (Telegram WebApp)
@routes.get(r"/app/{path:\S+}", allow_head=True)
async def mini_app_handler(request: web.Request):
    """
    Serve the Telegram Mini App interface
    URL format: /app/{file_id}?hash={secure_hash}
    """
    try:
        path = request.match_info["path"]
        
        # Extract file ID and hash
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            file_id = int(match.group(2))
        else:
            file_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        
        # Render the mini app page
        html = await render_mini_app(file_id, secure_hash)
        return web.Response(text=html, content_type="text/html")
        
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FileNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except Exception as e:
        logger.error(f"Mini app error: {e}")
        raise web.HTTPInternalServerError(text=str(e))


# API Endpoint - Get File Metadata (Audio tracks, Subtitles, Duration)
@routes.get("/api/metadata/{file_id}")
async def metadata_handler(request: web.Request):
    """
    Get file metadata including audio tracks and subtitles
    URL: /api/metadata/{file_id}?hash={secure_hash}
    
    Response:
    {
        "file_id": int,
        "file_name": str,
        "file_size": int,
        "duration": int (seconds),
        "audio_tracks": [
            {"index": 0, "language": "English", "name": "Audio 1", "codec": "aac"}
        ],
        "subtitles": [
            {"index": 0, "language": "English", "url": "/subtitle/{file_id}/{index}?hash={hash}"}
        ]
    }
    """
    try:
        file_id = int(request.match_info["file_id"])
        secure_hash = request.rel_url.query.get("hash")
        
        # Get the faster client
        index = min(work_loads, key=work_loads.get) if work_loads else 0
        faster_client = multi_clients[index]
        
        # Get file properties
        if faster_client in class_cache:
            tg_connect = class_cache[faster_client]
        else:
            tg_connect = ByteStreamer(faster_client)
            class_cache[faster_client] = tg_connect
        
        file_properties = await tg_connect.get_file_properties(file_id)
        
        # Validate hash
        if file_properties.unique_id[:6] != secure_hash:
            raise InvalidHash("Invalid file hash")
        
        # Build metadata response
        metadata = {
            "file_id": file_id,
            "file_name": file_properties.file_name or "Unknown",
            "file_size": file_properties.file_size,
            "mime_type": file_properties.mime_type,
            "audio_tracks": [
                {
                    "index": 0,
                    "language": "English",
                    "name": "Default Audio",
                    "codec": "aac"
                }
            ],
            "subtitles": []
        }
        
        # Note: To implement actual audio/subtitle extraction,
        # you would need to use ffprobe or similar tools
        # For now, returning template structure
        
        return web.json_response(metadata)
        
    except InvalidHash as e:
        raise web.HTTPForbidden(json.dumps({"error": "Invalid hash"}))
    except FileNotFound as e:
        raise web.HTTPNotFound(json.dumps({"error": "File not found"}))
    except Exception as e:
        logger.error(f"Metadata error: {e}")
        raise web.HTTPInternalServerError(json.dumps({"error": str(e)}))


# API Endpoint - Stream subtitle file
@routes.get(r"/subtitle/{file_id}/{index}")
async def subtitle_handler(request: web.Request):
    """
    Stream subtitle file
    URL: /subtitle/{file_id}/{index}?hash={secure_hash}
    """
    try:
        file_id = int(request.match_info["file_id"])
        subtitle_index = int(request.match_info["index"])
        secure_hash = request.rel_url.query.get("hash")
        
        # Validate and fetch subtitle
        # This would need to be implemented with actual subtitle extraction
        
        raise web.HTTPNotFound(text="Subtitle not found")
        
    except Exception as e:
        logger.error(f"Subtitle error: {e}")
        raise web.HTTPInternalServerError(text=str(e))


# Health Check
@routes.get("/api/health")
async def health_check(_):
    """Simple health check endpoint"""
    return web.json_response({
        "status": "ok",
        "mini_app": "enabled"
    })

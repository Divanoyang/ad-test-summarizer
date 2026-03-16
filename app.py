"""自动驾驶泛化测试问题总结 Web 服务。"""

import json
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import settings
from summarizer import summarize, summarize_stream

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ad-summarizer")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("服务启动 | model=%s | port=%d", settings.LLM_MODEL, settings.PORT)
    yield
    logger.info("服务关闭")


app = FastAPI(title="自动驾驶泛化测试问题总结", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    text: str
    model: str | None = None


class SummarizeResponse(BaseModel):
    markdown: str
    elapsed_ms: int
    model: str


@app.get("/api/models")
async def api_models():
    return {"models": settings.get_model_list()}


@app.post("/api/summarize", response_model=SummarizeResponse)
async def api_summarize(req: SummarizeRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "输入不能为空")
    if len(text) < 10:
        raise HTTPException(400, "输入内容过短，请粘贴完整的问题记录")

    use_model = req.model or settings.LLM_MODEL
    t0 = time.monotonic()
    try:
        result = await summarize(text, model=use_model)
    except Exception:
        logger.exception("LLM 调用失败 | model=%s", use_model)
        raise HTTPException(502, f"模型 {use_model} 调用失败，请换一个模型重试")

    elapsed = int((time.monotonic() - t0) * 1000)
    logger.info("总结完成 | model=%s | 输入长度=%d | 耗时=%dms", use_model, len(text), elapsed)
    return SummarizeResponse(markdown=result, elapsed_ms=elapsed, model=use_model)


@app.post("/api/summarize/stream")
async def api_summarize_stream(req: SummarizeRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "输入不能为空")
    if len(text) < 10:
        raise HTTPException(400, "输入内容过短，请粘贴完整的问题记录")

    use_model = req.model or settings.LLM_MODEL

    async def event_generator():
        t0 = time.monotonic()
        try:
            async for chunk in summarize_stream(text, model=use_model):
                yield {"event": "chunk", "data": json.dumps({"text": chunk}, ensure_ascii=False)}
            elapsed = int((time.monotonic() - t0) * 1000)
            yield {"event": "done", "data": json.dumps({"model": use_model, "elapsed_ms": elapsed}, ensure_ascii=False)}
            logger.info("流式总结完成 | model=%s | 输入长度=%d | 耗时=%dms", use_model, len(text), elapsed)
        except Exception:
            logger.exception("LLM 流式调用失败 | model=%s", use_model)
            yield {"event": "error", "data": json.dumps({"detail": f"模型 {use_model} 调用失败"}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())


@app.get("/")
async def index():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.LLM_MODEL}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)

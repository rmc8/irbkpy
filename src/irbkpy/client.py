from __future__ import annotations

import asyncio
import logging
import time
from types import TracebackType
from typing import Any

import httpx

from .cache import IRBankCache
from .config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, resolve_api_key
from .exceptions import RateLimitError, raise_for_status
from .services import (
    AsyncDisclosuresService,
    AsyncDividendsService,
    AsyncFinancialsService,
    AsyncIndicatorsService,
    AsyncIndustriesService,
    AsyncOrganizationsService,
    AsyncPeersService,
    AsyncPersonsService,
    AsyncRankingsService,
    AsyncScreeningService,
    AsyncSecuritiesService,
    AsyncSegmentsService,
    AsyncShareholdersService,
    AsyncUsageService,
    AsyncValuationsService,
    DisclosuresService,
    DividendsService,
    FinancialsService,
    IndicatorsService,
    IndustriesService,
    OrganizationsService,
    PeersService,
    PersonsService,
    RankingsService,
    ScreeningService,
    SecuritiesService,
    SegmentsService,
    ShareholdersService,
    UsageService,
    ValuationsService,
)

USER_AGENT = "irbkpy/0.1.1"
logger = logging.getLogger("irbkpy")


class IRBankClient:
    """IRBank APIの同期通信クライアントです。

    銘柄情報、財務データ、適時開示、スクリーニングなど各機能へのアクセサを提供します。
    with構文を用いることで、処理終了時にコネクションを自動で切断します。
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
        enable_cache: bool = False,
        cache_ttl: int = 86400,
        cache_path: str | None = None,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ) -> None:
        """同期クライアントを初期化します。

        引数api_keyが未指定の場合は、環境変数IRBK_API_KEYや.envファイルから自動解決します。
        enable_cacheを有効化すると、SQLiteによるローカルキャッシュを活用してリクエスト枠を節約します。
        max_retriesおよびretry_backoffにより、短時間バースト制限（HTTP 429）発生時の自動待機・再試行を設定できます。
        """
        self.api_key = resolve_api_key(api_key)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.cache = (
            IRBankCache(db_path=cache_path, default_ttl=cache_ttl) if enable_cache else None
        )

        req_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if headers:
            req_headers.update(headers)

        if http_client is not None:
            self._client = http_client
            for k, v in req_headers.items():
                if k.lower() not in [h.lower() for h in self._client.headers]:
                    self._client.headers[k] = v
        else:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=req_headers,
                timeout=timeout,
            )
        self._owns_client = http_client is None

        # 各ドメイン別サービスクラスの初期化
        self.securities = SecuritiesService(self)
        self.organizations = OrganizationsService(self)
        self.industries = IndustriesService(self)
        self.financials = FinancialsService(self)
        self.indicators = IndicatorsService(self)
        self.segments = SegmentsService(self)
        self.dividends = DividendsService(self)
        self.valuations = ValuationsService(self)
        self.peers = PeersService(self)
        self.shareholders = ShareholdersService(self)
        self.persons = PersonsService(self)
        self.disclosures = DisclosuresService(self)
        self.screening = ScreeningService(self)
        self.rankings = RankingsService(self)
        self.usage = UsageService(self)

    def _build_url(self, path: str) -> str:
        """指定された相対パスから完全なリクエストURLを組み立てます。"""
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GETリクエストを送信し、JSON応答を返却します。

        キャッシュが有効化されている場合、利用枠確認（/usage）を除いて
        ローカルキャッシュの照会および保存を透過的に行います。
        短時間バースト制限（HTTP 429）を受信した場合は指数バックオフで自動再試行します。
        """
        url = self._build_url(path)
        cache_key = None
        # 残量照会エンドポイントは最新値を取得するためキャッシュ対象外とする
        if self.enable_cache and self.cache and not path.rstrip("/").endswith("/usage"):
            cache_key = self.cache.build_key(url, params)
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug("キャッシュにヒットしました: %s", url)
                return cached

        attempt = 0
        while True:
            logger.debug(
                "APIリクエストを送信します: %s params=%s (試行%d)", url, params, attempt + 1
            )
            response = self._client.get(url, params=params)
            try:
                data = response.json()
            except Exception:
                data = None

            try:
                raise_for_status(response.status_code, data, raw_response=response)
                break
            except RateLimitError as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise e
                # Retry-Afterヘッダーの確認
                retry_after_str = response.headers.get("Retry-After")
                try:
                    wait_sec = (
                        float(retry_after_str)
                        if retry_after_str
                        else self.retry_backoff * (2 ** (attempt - 1))
                    )
                except ValueError:
                    wait_sec = self.retry_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "レート制限を受信しました。%.1f秒待機後に再試行します（試行%d/%d）",
                    wait_sec,
                    attempt,
                    self.max_retries,
                )
                time.sleep(wait_sec)

        if cache_key and self.cache and response.status_code == 200 and isinstance(data, dict):
            self.cache.set(cache_key, data, status_code=response.status_code)

        return data if isinstance(data, dict) else {}

    def clear_cache(self) -> None:
        """ローカルに保存されているすべての応答キャッシュを破棄します。"""
        if self.cache:
            self.cache.clear()

    def close(self) -> None:
        """HTTPクライアントの接続セッションを終了します。"""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> IRBankClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()


class AsyncIRBankClient:
    """IRBank APIの非同期通信クライアントです。

    async/await構文を用いて、並行処理やFastAPI等の非同期基盤から安全に呼び出せます。
    async with構文に対応しています。
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
        enable_cache: bool = False,
        cache_ttl: int = 86400,
        cache_path: str | None = None,
        max_retries: int = 3,
        retry_backoff: float = 2.0,
    ) -> None:
        """非同期クライアントを初期化します。

        引数api_keyが未指定の場合は、環境変数IRBK_API_KEYや.envファイルから自動解決します。
        enable_cacheを有効化すると、SQLiteによるローカルキャッシュを活用してリクエスト枠を節約します。
        max_retriesおよびretry_backoffにより、短時間バースト制限（HTTP 429）発生時の自動待機・再試行を設定できます。
        """
        self.api_key = resolve_api_key(api_key)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.cache = (
            IRBankCache(db_path=cache_path, default_ttl=cache_ttl) if enable_cache else None
        )

        req_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if headers:
            req_headers.update(headers)

        if http_client is not None:
            self._client = http_client
            for k, v in req_headers.items():
                if k.lower() not in [h.lower() for h in self._client.headers]:
                    self._client.headers[k] = v
        else:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=req_headers,
                timeout=timeout,
            )
        self._owns_client = http_client is None

        # 各ドメイン別非同期サービスクラスの初期化
        self.securities = AsyncSecuritiesService(self)
        self.organizations = AsyncOrganizationsService(self)
        self.industries = AsyncIndustriesService(self)
        self.financials = AsyncFinancialsService(self)
        self.indicators = AsyncIndicatorsService(self)
        self.segments = AsyncSegmentsService(self)
        self.dividends = AsyncDividendsService(self)
        self.valuations = AsyncValuationsService(self)
        self.peers = AsyncPeersService(self)
        self.shareholders = AsyncShareholdersService(self)
        self.persons = AsyncPersonsService(self)
        self.disclosures = AsyncDisclosuresService(self)
        self.screening = AsyncScreeningService(self)
        self.rankings = AsyncRankingsService(self)
        self.usage = AsyncUsageService(self)

    def _build_url(self, path: str) -> str:
        """指定された相対パスから完全なリクエストURLを組み立てます。"""
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """非同期GETリクエストを送信し、JSON応答を返却します。

        キャッシュが有効化されている場合、利用枠確認（/usage）を除いて
        ローカルキャッシュの照会および保存を透過的に行います。
        短時間バースト制限（HTTP 429）を受信した場合は指数バックオフで自動再試行します。
        """
        url = self._build_url(path)
        cache_key = None
        # 残量照会エンドポイントは最新値を取得するためキャッシュ対象外とする
        if self.enable_cache and self.cache and not path.rstrip("/").endswith("/usage"):
            cache_key = self.cache.build_key(url, params)
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug("キャッシュにヒットしました: %s", url)
                return cached

        attempt = 0
        while True:
            logger.debug(
                "APIリクエストを非同期送信します: %s params=%s (試行%d)", url, params, attempt + 1
            )
            response = await self._client.get(url, params=params)
            try:
                data = response.json()
            except Exception:
                data = None

            try:
                raise_for_status(response.status_code, data, raw_response=response)
                break
            except RateLimitError as e:
                attempt += 1
                if attempt > self.max_retries:
                    raise e
                retry_after_str = response.headers.get("Retry-After")
                try:
                    wait_sec = (
                        float(retry_after_str)
                        if retry_after_str
                        else self.retry_backoff * (2 ** (attempt - 1))
                    )
                except ValueError:
                    wait_sec = self.retry_backoff * (2 ** (attempt - 1))
                logger.warning(
                    "レート制限を受信しました。%.1f秒待機後に再試行します（試行%d/%d）",
                    wait_sec,
                    attempt,
                    self.max_retries,
                )
                await asyncio.sleep(wait_sec)

        if cache_key and self.cache and response.status_code == 200 and isinstance(data, dict):
            self.cache.set(cache_key, data, status_code=response.status_code)

        return data if isinstance(data, dict) else {}

    def clear_cache(self) -> None:
        """ローカルに保存されているすべての応答キャッシュを破棄します。"""
        if self.cache:
            self.cache.clear()

    async def aclose(self) -> None:
        """非同期HTTPクライアントの接続セッションを終了します。"""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncIRBankClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

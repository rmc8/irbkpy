from __future__ import annotations

from ..models.persons import (
    OfficersResponse,
    PersonAppointmentsResponse,
    PersonCompensationResponse,
    PersonHoldingsResponse,
    PersonProfile,
)
from .base import AsyncService, SyncService


class PersonsService(SyncService):
    """役員・人物情報ドメインの同期サービスクラス

    役員の就任履歴、役員報酬履歴、自社株および他社株の保有状況などを取得します。
    """

    def get(self, person_id: str) -> PersonProfile:
        """指定した人物IDの基本プロフィールを取得します。

        氏名、生年月日、現任の役職一覧などを返します。
        """
        data = self._client._get(f"/persons/{person_id}")
        return PersonProfile.model_validate(data)

    def get_appointments(self, person_id: str) -> PersonAppointmentsResponse:
        """指定した人物IDの就任履歴を取得します。

        歴代の役員就任先企業名、役職、任期などを返します。
        """
        data = self._client._get(f"/persons/{person_id}/appointments")
        return PersonAppointmentsResponse.model_validate(data)

    def get_compensation_history(self, person_id: str) -> PersonCompensationResponse:
        """指定した人物IDの役員報酬履歴を取得します。

        各社からの役員報酬総額、固定報酬、業績連動報酬、株式報酬などの期別内訳を返します。
        """
        data = self._client._get(f"/persons/{person_id}/compensation-history")
        return PersonCompensationResponse.model_validate(data)

    def get_holdings(self, person_id: str) -> PersonHoldingsResponse:
        """指定した人物IDの株式保有推移を取得します。

        保有企業別の保有株式数や持株比率の期別推移を返します。
        """
        data = self._client._get(f"/persons/{person_id}/holdings")
        return PersonHoldingsResponse.model_validate(data)

    def list_officers(self, code: str) -> OfficersResponse:
        """指定した銘柄コードに所属する役員一覧を取得します。

        役員名、役職、社外役員フラグ、任期などを返します。
        """
        data = self._client._get(f"/securities/{code}/officers")
        return OfficersResponse.model_validate(data)


class AsyncPersonsService(AsyncService):
    """役員・人物情報ドメインの非同期サービスクラス

    非同期通信によって役員のプロフィール、就任履歴、報酬、株式保有状況を取得します。
    """

    async def get(self, person_id: str) -> PersonProfile:
        """指定した人物IDの基本プロフィールを非同期で取得します。"""
        data = await self._client._get(f"/persons/{person_id}")
        return PersonProfile.model_validate(data)

    async def get_appointments(self, person_id: str) -> PersonAppointmentsResponse:
        """指定した人物IDの就任履歴を非同期で取得します。"""
        data = await self._client._get(f"/persons/{person_id}/appointments")
        return PersonAppointmentsResponse.model_validate(data)

    async def get_compensation_history(self, person_id: str) -> PersonCompensationResponse:
        """指定した人物IDの役員報酬履歴を非同期で取得します。"""
        data = await self._client._get(f"/persons/{person_id}/compensation-history")
        return PersonCompensationResponse.model_validate(data)

    async def get_holdings(self, person_id: str) -> PersonHoldingsResponse:
        """指定した人物IDの株式保有推移を非同期で取得します。"""
        data = await self._client._get(f"/persons/{person_id}/holdings")
        return PersonHoldingsResponse.model_validate(data)

    async def list_officers(self, code: str) -> OfficersResponse:
        """指定した銘柄コードに所属する役員一覧を非同期で取得します。"""
        data = await self._client._get(f"/securities/{code}/officers")
        return OfficersResponse.model_validate(data)

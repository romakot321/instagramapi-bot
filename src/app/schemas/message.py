from aiogram import types
from pydantic import BaseModel, ConfigDict, computed_field, Field


class Message(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message_id: int | None = (
        None  # message_id used for edit, get it from telegram response
    )


class TextMessage(Message):
    text: str
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None
    parse_mode: str | None = None


class MediaMessage(Message):
    caption: str | None = None
    document: types.BufferedInputFile | str
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None
    parse_mode: str | None = None

    @computed_field
    @property
    def media(self) -> types.InputMediaDocument:
        return types.InputMediaDocument(
            media=self.document, caption=self.caption, parse_mode=self.parse_mode
        )


class VideoMessage(Message):
    caption: str | None = None
    video: types.BufferedInputFile | str
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None
    parse_mode: str | None = None

    @computed_field
    @property
    def media(self) -> types.InputMediaVideo:
        return types.InputMediaVideo(
            media=self.video, caption=self.caption, parse_mode=self.parse_mode
        )


class PhotoMessage(Message):
    caption: str | None = None
    photo: types.BufferedInputFile | types.FSInputFile | str
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None
    parse_mode: str | None = None

    @computed_field
    @property
    def media(self) -> types.InputMediaPhoto:
        return types.InputMediaPhoto(
            media=self.photo, caption=self.caption, parse_mode=self.parse_mode
        )


class MediaGroupMessage(Message):
    caption: str | None = None
    files_: list[bytes | str] = Field(validation_alias="files")
    parse_mode: str | None = None
    reply_markup: types.InlineKeyboardMarkup | types.ReplyKeyboardMarkup | None = None

    @computed_field
    @property
    def media(self) -> list[types.InputMediaPhoto]:
        if not self.files_:
            return []
        media = [
            types.InputMediaPhoto(
                media=(types.BufferedInputFile(self.files_[0], filename="file") if isinstance(self.files_[0], bytes) else self.files_[0]),
                caption=self.caption,
                parse_mode=self.parse_mode,
            )
        ]
        return media + [
            types.InputMediaPhoto(
                media=types.BufferedInputFile(file, filename="file") if isinstance(file, bytes) else file
            )
            for file in self.files_[1:]
        ]

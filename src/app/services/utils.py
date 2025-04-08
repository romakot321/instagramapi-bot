from aiogram.methods import EditMessageText, EditMessageMedia, SendPhoto, SendVideo
from aiogram.methods import SendMessage, SendDocument, SendMediaGroup
from aiogram.types import CallbackQuery, Message

from app.schemas.message import PhotoMessage, TextMessage, MediaMessage, MediaGroupMessage, VideoMessage

__message_type_to_send_method: dict = {
    TextMessage: SendMessage,
    MediaMessage: SendDocument,
    MediaGroupMessage: SendMediaGroup,
    VideoMessage: SendVideo,
    PhotoMessage: SendPhoto
}
__message_type_to_edit_method: dict = {
    TextMessage: EditMessageText,
    MediaMessage: EditMessageMedia,
    VideoMessage: EditMessageMedia,
    PhotoMessage: EditMessageMedia
}


def build_aiogram_method(
        chat_id: int | None,
        message: TextMessage | MediaMessage | PhotoMessage | VideoMessage,
        use_edit: bool | None = None,
        tg_object: CallbackQuery | Message | None = None
) -> SendMessage | SendDocument:
    """Return None if unknown message type"""
    if chat_id is None and tg_object is None:
        raise ValueError("Specify chat id for method build")
    chat_id = chat_id or tg_object.from_user.id

    if use_edit is not False and isinstance(tg_object, CallbackQuery):
        message.message_id = tg_object.message.message_id
        method = __message_type_to_edit_method.get(type(message))
    elif use_edit:
        method = __message_type_to_edit_method.get(type(message))
    else:
        method = __message_type_to_send_method.get(type(message))
    if method is None:
        raise ValueError("Unknown message type")
    return method(chat_id=chat_id, **message.model_dump())

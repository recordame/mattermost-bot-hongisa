from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to


class Help(Plugin):
    @listen_to("^명령어$")
    async def help(self, message: Message):
        self.driver.direct_message(
            message.user_id,
            "- **날씨**\n"
            "   - 날씨 {지역}\n"
            "   - 날씨알림 {지역}\n"
            "   - 날씨알림시작 {지역} {7(시)} {12(시)}\n"
            "   - 날씨알림종료\n"
            "- **꼬들**\n"
            "   - 꼬들알림시작 {7(시)} {20(분)}\n"
            "   - 꼬들알림종료\n"
            "- **미사**\n"
            "   - 미사알림시작 {11(시-주일)}\n"
            "   - 미사알림종료\n"
        )

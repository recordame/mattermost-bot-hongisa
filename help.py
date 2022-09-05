from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to


class Help(Plugin):
    @listen_to("^명령어$")
    async def help(self, message: Message):
        self.driver.direct_message(
            message.user_id,
            "- 날씨\n"
            "   - 날씨 {지역}\n"
            "   - 날씨알림 {지역}\n"
            "   - 날씨알림시작 {지역} {1(시간마다)}\n"
            "   - 날씨알림종료\n"
            "- 꼬들알림\n"
            "   - 꼬들알림예약 {7(알림시간)}\n"
            "   - 꼬들알림종료\n"
            "- 미사알림\n"
            "   - 미사알림예약 {11(주일미사시간)}\n"
            "   - 미사알림종료\n"
        )

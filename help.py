from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to


class Help(Plugin):
    @listen_to("^명령어$")
    async def help(self, message: Message):
        self.driver.direct_message(
            message.user_id,
            "- 날씨\n"
            "   - 날씨 지역\n"
            "   - 날씨알림 1(시간마다)\n"
            "   - 날씨종료\n"
            "- 꼬들시작 7(해당시간)\n"
            "   - 꼬들종료"
        )

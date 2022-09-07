from mmpy_bot import Message
from mmpy_bot import Plugin, listen_to


class Help(Plugin):
    @listen_to("^명령어")
    async def help(self, message: Message):
        self.driver.direct_message(
            message.user_id,
            "- **날씨**\n"
            "   - 나에게만: `날씨` `{지역?}`\n"
            "   - 전체알림: `날씨알림` `{지역?}`\n"
            "   - 전체알림: `날씨알림예약` `{지역?}` `{7(시)}` `{12(시)}`\n"
            "   - 전체알림: `날씨알림예약취소`\n"
            "- **꼬들**\n"
            "   - 전체알림: `꼬들알림`\n"
            "   - 전체알림: `꼬들알림예약` `{7(시)}` `{20(분)}`\n"
            "   - 전체알림: `꼬들알림예약취소`\n"
            "- **미사**\n"
            "   - 나에게만: `미사`\n"
            "   - 전체알림: `미사알림예약` `{10(시-주일)}`\n"
            "   - 전체알림: `미사알림예약취소`\n"
            "- **복약**\n"
            "   - 전체알림: `복약알림예약` `{7(시) 20(시) 30(분)}`\n"
            "   - 전체알림: `복약알림예약취소`\n"
            "- **알림목록**\n"
        )

from mmpy_bot import Message, Plugin, listen_to


class Help(Plugin):
    @listen_to("테스트")
    def hello_click(self, message: Message):
        response = message.body.__str__()
        self.driver.reply_to(message, response)
        self.driver.reply_to()

    @listen_to("^명령어$")
    async def help(self, message: Message):
        self.driver.direct_message(
            message.user_id,
            "**채널알람**\n"
            "- **날씨**\n"
            "   - `날씨` `{지역}`\n"
            "   - `날씨알람예약` `{지역}` `{시1,시2}` `{분}` `{채널ID}`\n"
            "   - `날씨알람취소`\n"
            "- **꼬들**\n"
            "   - `꼬들알람` `{채널ID}`\n"
            "   - `꼬들알람예약` `{시}` `{분}` `{채널ID}`\n"
            "   - `꼬들알람취소` `{채널ID}`\n"
            "- **미사**\n"
            "   - `미사`\n"
            "   - `미사알람예약` `{시}` `{분}` `{채널ID}`\n"
            "   - `미사알람취소` `{채널ID}`\n"
            "- **복약**\n"
            "   - `복약알람예약` `{시1,시2}` `{분}` `{채널ID}`\n"
            "   - `복약알람취소` `{채널ID}`\n"
            "\n"
            "**개인알람**\n"
            "   - `개인알람등록` `{규칙명}` `{요일}` `{시}` `{분}` `{초}` `{출력 메시지}`\n"
            "     - 예)`개인알람등록` `rest` `mon-fri` `9-17` `50` `0` `지금부터 10분간 휴식!`\n"
            "   - `개인알람취소 {규칙명}`\n"
            "\n"
            "**부가기능**\n"
            "- `환율`\n"
            "- `알람목록`\n"
            "- `알람저장`\n"
            "- `알람복원`\n"
        )

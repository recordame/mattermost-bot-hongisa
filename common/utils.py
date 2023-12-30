import mmpy_bot


def update_post(driver: mmpy_bot.driver, post_id: str, new_message: str):
    req_data: dict = {
        'id': post_id,
        'message': new_message
    }

    driver.posts.update_post(post_id, options=req_data)


def display_progress(current_step, total_steps):
    progress_bar: str = ''

    for i in range(0, current_step):
        progress_bar += '■'

    for i in range(current_step, total_steps):
        progress_bar += '□'

    return progress_bar

# 分页处理
def paginate_data(data, limit, page):
    limit = int(limit)
    page = int(page)
    total_count = len(data)
    total_page = (total_count + limit - 1) // limit
    start_index = (page - 1) * limit
    end_index = start_index + limit

    code = 'SUCCESS'
    message = 'Success'

    if page < 1:
        code = 'FAILED'
        message = 'page < 1'
    elif page > total_page:
        code = 'FAILED'
        message = f'page > total_page = {total_page}'

    return data[start_index:end_index], total_count, total_page, code, message
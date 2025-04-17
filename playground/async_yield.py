import asyncio

async def async_generator():
    for i in range(5):
        await asyncio.sleep(1)  # 模拟异步操作
        yield i

async def main():
    async for value in async_generator():
        print(value)

# 运行事件循环
asyncio.run(main())


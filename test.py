import asyncio

async def func1():
    print("func1")
    await asyncio.sleep(2)
    print("func1 again")

async def func2():
    print("func2")
    await asyncio.sleep(4)
    print("func2 again")

async def func3():
    asyncio.gather(func1(), func2())

async def main():
    print("main")
    await asyncio.gather(func1(), func2(), func3())
    print("done")
    #await func1()
    #await func2()

if __name__ == "__main__":
    asyncio.run(main())
# async / await
# -------------

# async/await alone doesn't make things run concurrently — it just makes them non-blocking.
# If you await each coroutine one after the other, they still run sequentially.

# async gives you concurrency (juggling tasks), not parallelism (doing tasks simultaneously).

# -----------------------------------------------------------------------------------------------
import time, math, random


def calc1():
    print("calc1")
    ans = [round(math.sqrt(i), 2) for i in range(1, 10000)]
    time.sleep(2)  # blocks execution
    return ans


def calc2():
    print("calc2")
    ans = [random.randint(1, 10000) for i in range(1, 10000)]
    time.sleep(2)  # blocks execution
    return ans


def main():
    start = time.time()
    c1 = calc1()
    c2 = calc2()
    end = time.time() - start
    print(f"Time taken to execute : {round(end, 2)} seconds")

main()


#-----------------
#Without Blocking
#-----------------
import asyncio


async def calc3():
    print("calc3")
    ans = [round(math.sqrt(i), 2) for i in range(1, 10000)]
    await asyncio.sleep(2)  # await command is the yield.
    return ans


async def calc4():
    print("calc4")
    ans = [random.randint(1, 10000) for i in range(1, 10000)]
    await asyncio.sleep(2)
    return ans


async def main():
    start = time.time()
    c3, c4 = await asyncio.gather(calc3(), calc4())
    end = time.time() - start
    print(f"Time taken to execute : {round(end, 2)} seconds")

    return c3, c4

c3,c4 = asyncio.run(main())

async def strOps1():
    s1 = "Hello"
    s2 = "World"
    result = s1 + " " + s2
    await asyncio.sleep(2)
    return result

async def strOps2():
    text = "apple,banana,cherry"
    fruits = text.split(",")  # ["apple", "banana", "cherry"]
    joined = "-".join(fruits)  # "apple-banana-cherry"
    await asyncio.sleep(2)
    return joined


async def main():
    start = time.time()
    st1, st2 = await asyncio.gather(strOps1(), strOps2())
    end = time.time() - start
    print(f"Time taken to execute : {round(end, 2)} seconds")

    return st1, st2


st1, st2 = asyncio.run(main())
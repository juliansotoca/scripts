#http://superuser.com/questions/443406/how-can-i-produce-high-cpu-load-on-a-linux-server
from multiprocessing import Pool

def f(x):
    # Put any cpu (only) consuming operation here. I have given 1 below -
    while True:
        x * x

# decide how many cpus you need to load with.
no_of_cpu_to_be_consumed = 8

p = Pool(processes=no_of_cpu_to_be_consumed)
p.map(f, range(no_of_cpu_to_be_consumed))

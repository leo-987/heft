import heft
import cpop

heft_scheduler = heft.HEFT('input.txt')
heft_scheduler.run()
heft_scheduler.display_result()

cpop_scheduler = cpop.CPOP('input.txt')
cpop_scheduler.run()
cpop_scheduler.display_result()
Ticket Write-up:

Summary: difficult to estimate our distance from our current metrics – unless we can extract velocity or acceleration from our data, since distance is most directly related to velocity, acceleration, and time:
Distance = Speed × Time (d = s × t)
d = v1t + 1.5at^2
(Vx)^2 = (Vo)^2 + 2ad

First idea: We estimate the distance they have covered based on the percentage the run completed. Since we have the total time it took for the run (0ms to the last to_time for the run) and the current time (to_time of the current stride), we can create a percentage of the run completed in terms of time (current time/total time _ 100). We can then use that percentage to estimate the percentage of the run completed in terms of distance (pct/100 _ total distance).

Problem: Sprinters will not cover distance at a constant rate. The acceleration out of the block might take 10sec out of the 30sec sprint (33.33%), but only 10m out of the 100m (10%) was covered.

Solution: We need a correction factor based on the GCT to FT ratio (lower FT:GCT ratio = accelerating/deaccelerating, and therefore a lower correction factor because you are covering less distance)
Don’t actually have to account for height since longer acceleration periods are accounted for in ratio and are automatically weighted less
Correction factor = FT / GCT

Final Equation: (to_time / total_time) x total_dist x correction_factor

Other possible solutions:
Linear regression model to predict position, but would need to fine tune constants (correction_factor/slope) and need a training set of data
Have split times (know when the runner hits 10m, 20m, etc.) to calculate a velocity from those times, but it might not be accurate as acceleration over the period might not be linear and the data points might not be close enough together
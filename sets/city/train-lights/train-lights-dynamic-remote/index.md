---
title: "Train with lights and a dynamic and optional remote"
maintainer:
    user: "hwillemen"
    name: "Hans Willemen"
image:
    local: "train-with-lights.jpg"
description:
    "A train with lights that can be started to the previous settings, 
	paused and stopped without a remote. 
	On any point in time a remote can be connected to change speed and/or 
	brightness."
building_instructions:
    external:
    - https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6179158.pdf
    - https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6216989.pdf
code: "#program"

---

## Design modifications
Build the Winter Holiday Train using the standard instructions.
Any other train can be used as well.
On port A, connect the [Train motor][dcmotor].
On port B, connect a [PUP light][light] or a modified light kit that acts as one.
Below, you can see an example of such custom hardware that simulates a light.

![](example-pup-dummy.jpg)

## Program

This program starts the train in the last known speed and brightness settings.
No remote required, so also useful for large layouts.
With a short press the motor is paused (lights stay on).
Another short press starts the motor in the last settings again.
A press of about 2 seconds stops the script.
A press of about 5 seconds (> 4.5) turns the hub off.

During operation, at any point a remote can be connected to change speed or brightness.
Remote presence is checked every 10 seconds and can take about 4-5 seconds.
In busy bleutooth environments it is advised to name your remote and to connect by name.

{% include copy-code.html %}
```python
{% include_relative pup_train.py %}
```

[dcmotor]: https://docs.pybricks.com/en/latest/pupdevices/dcmotor.html
[light]: https://docs.pybricks.com/en/latest/pupdevices/light.html


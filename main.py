from machine import Pin, Timer, SoftI2C
from time import sleep_ms
import ssd1306
from hcsr04 import HCSR04

button_pin = Pin(13, Pin.IN, Pin.PULL_UP)

led_back_1 = Pin(16, Pin.OUT)  
led_back_2 = Pin(2, Pin.OUT)
led_left_1 = Pin(26, Pin.OUT)
led_left_2 = Pin(27, Pin.OUT)
led_right_1 = Pin(33, Pin.OUT)  
led_right_2 = Pin(25, Pin.OUT)

sensor = HCSR04(trigger_pin=4, echo_pin=5, echo_timeout_us=20000)
sensor_left = HCSR04(trigger_pin=12, echo_pin=14, echo_timeout_us=20000)
sensor_right = HCSR04(trigger_pin=16, echo_pin=17, echo_timeout_us=20000)  

i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
i2c_side = SoftI2C(sda=Pin(18), scl=Pin(19)) 
oled_side = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_side)

system_on = False

def button_pressed(pin):
    global system_on
    system_on = not system_on  
    if system_on:
        print("ระบบเปิดทำงาน")
    else:
        print("ระบบปิดทำงาน")
        led_back_1.value(0)
        led_back_2.value(0)
        led_left_1.value(0)
        led_left_2.value(0)
        led_right_1.value(0)
        led_right_2.value(0)
        oled.fill(0)   
        oled.show()

button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

timer = Timer(0)

def measure_and_display(timer):
    if system_on:
        distance_back = sensor.distance_cm()
        print('Distance (back):', distance_back, 'cm')
        distance_left = sensor_left.distance_cm()  
        print('Distance (left):', distance_left, 'cm')
        distance_right = sensor_right.distance_cm()  
        print('Distance (right):', distance_right, 'cm')
        
        oled.fill(0)
        oled.text(f"left : {distance_left:.2f} cm", 0, 0)
        oled.text(f"right: {distance_right:.2f} cm", 0, 10)
        oled.text(f"back : {distance_back:.2f} cm", 0, 20)
        oled.show()

        oled_side.fill(0)
        max_line_length = 100  
        line_spacing = 20
        center_x = oled_width // 2
        center_y = oled_height // 2
        car_width = 20
        car_height = 10
        
        oled_side.rect(center_x - car_width // 2, center_y - car_height // 2, car_width, car_height, 1)

        left_line_length = int(max_line_length * (distance_left / 100)) 
        oled_side.line(0, center_y, left_line_length, center_y, 1)
        
        right_line_length = int(max_line_length * (1 - distance_right / 100))
        oled_side.line(oled_width, center_y, oled_width - right_line_length, center_y, 1)
        
        bottom_line_length = int(max_line_length * (distance_back / 100)) 
        oled_side.line(center_x, oled_height, center_x, oled_height - bottom_line_length, 1)
        
        oled_side.show()

        control_leds(led_back_1, led_back_2, distance_back, 10, 20)  
        control_leds(led_left_1, led_left_2, distance_left, 10, 20)   
        control_leds(led_right_1, led_right_2, distance_right, 10, 20)

def control_leds(led1, led2, distance, threshold1, threshold2):
    if distance < threshold1:
        led1.value(1)
        led2.value(1)
    elif distance < threshold2:
        led1.value(1)
        led2.value(0)
    else:
        led1.value(0)
        led2.value(0)

timer.init(period=500, mode=Timer.PERIODIC, callback=measure_and_display)

while True:
    pass

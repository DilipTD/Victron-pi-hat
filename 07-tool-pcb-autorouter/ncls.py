# net classes for the relay extension: name, track, clearance, via_d, via_drill, nets, description
CLASSES=[
 ('Default', 0.25,0.20,0.6,0.3,[], 'LED drive and other low-current signals'),
 ('CONTACT', 2.00,0.50,0.8,0.4,['/CH%d_%s'%(n,f) for n in range(1,5) for f in ('COM','NO','NC')], 'relay contacts, 10 A SELV DC up to 30 V, 2.0 mm on F.Cu and B.Cu in parallel (1 oz)'),
 ('PWR_5V',  0.60,0.25,0.6,0.3,['+5V'], 'relay coils and LEDs from HAT +5V, about 0.3 A total'),
 ('COIL',    0.40,0.25,0.6,0.3,['/OUT1','/OUT2','/OUT3','/OUT4'], 'ULN2003 low-side coil drive, 71 mA each'),
]
def cls_of(net):
    for c in CLASSES[1:]:
        if net in c[5]: return c
    return CLASSES[0]

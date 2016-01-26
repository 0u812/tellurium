

.. code:: python


Simple Example
~~~~~~~~~~~~~~

.. code:: python

    import tellurium as te
    r = te.loada('S1 -> S2; k1*S1; k1 = 0.1; S1 = 10')
    r.simulate(0, 10, 100)
    r.plot()



.. image:: _notebooks/core/introduction_files/introduction_3_0.png


More Complex Example
~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import tellurium as te
    r = te.loada ('''
        # A dollar symbol means fix the species concentration
        J1: $S1 -> S2;  k1*S1; 
        J2: S2 -> S3;  k2*S2 - k3*S3;
        J3: S3 -> $S4; k4*S3;
    
        k1 = 0.1; k2 = 0.5; k3 = 0.5; k4 = 0.5;
        S1 = 10;
    ''')
    
    result = r.simulate (0, 10, 100, ['time', 'S1', 'S2', 'S3', 'J1'])
    r.plot(result);



.. image:: _notebooks/core/introduction_files/introduction_5_0.png


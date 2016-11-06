import numpy as np
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator


class CloseToOne(mscale.ScaleBase):
    name = 'close_to_one'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.nines = kwargs.get('nines', 5)

    def get_transform(self):
        return self.Transform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(FixedLocator(
            np.array([1 - 10**(-k) for k in range(1 + self.nines)])))
        axis.set_major_formatter(FixedFormatter(
            [str(1 - 10**(-k)) for k in range(1 + self.nines)]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min(1 - 10**(-self.nines), vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > 1 - 10**(-1 - self.nines), a)
            if masked.mask.any():
                return -ma.log10(1 - a)
            else:
                return -np.log10(1 - a)

        def inverted(self):
            return CloseToOne.InvertedTransform(self.nines)

    class InvertedTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            return 1. - 10**(-a)

        def inverted(self):
            return CloseToOne.Transform(self.nines)

mscale.register_scale(CloseToOne)


def test():
    with open('results/ext4/go-pg/10c-10r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])
    maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])
    times = [int(x[1]) - start for x in lines]
    latencies = [int(x[3]) for x in lines]
    data = latencies

    import pylab
    pylab.figure(figsize=(20, 9))
    t = np.array(data)
    pylab.subplot(121)
    pylab.plot(t)
    pylab.subplot(122)
    pylab.plot(t)
    pylab.yscale('close_to_one')

    pylab.grid(True)
    pylab.show()

if __name__ == '__main__':
    test()

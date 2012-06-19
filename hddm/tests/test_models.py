from __future__ import division
from copy import copy

import unittest
from nose import SkipTest

import hddm
from hddm.diag import check_model

def diff_model(param, subj=True, num_subjs=10, change=.5, samples=500):
    params_cond_a = {'v':.5, 'a':2., 'z':.5, 't': .3, 'T':0., 'V':0., 'Z':0.}
    params_cond_b = copy(params_cond_a)
    params_cond_b[param] += change

    params = {'A': params_cond_a, 'B': params_cond_b}

    data, subj_params = hddm.generate.gen_rand_data(params, subjs=num_subjs, samples=samples)

    model = hddm.model.HDDM(data, depends_on={param:['condition']}, is_group_model=subj)

    return model

class TestMulti(unittest.TestCase):
    def runTest(self):
        pass

    def test_diff_v(self, samples=1000):
        m = diff_model('v', subj=False, change=.5, samples=samples)
        return m

    def test_diff_a(self, samples=1000):
        m = diff_model('a', subj=False, change=-.5, samples=samples)
        return m

    def test_diff_a_subj(self, samples=1000):
        raise SkipTest("Disabled.")
        m = diff_model('a', subj=True, change=-.5, samples=samples)
        return m

class TestSingleBreakdown(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSingleBreakdown, self).__init__(*args, **kwargs)

        self.samples = 5000
        self.burn = 2500

    def runTest(self):
        return

    def test_HDDM(self, assert_=False):
        includes = [[], ['z'],['z', 'V'],['z', 'T'],['z', 'Z'], ['z', 'Z','T'], ['z', 'Z','T','V']]
        for include in includes:
            params = hddm.generate.gen_rand_params(include=include)
            data, params_true = hddm.generate.gen_rand_data(params, samples=500, subjs=1)
            model = hddm.model.HDDM(data, include=include, bias='z' in include, is_group_model=False)
            model.map()
            model.sample(self.samples, burn=self.burn)
            check_model(model.mc, params_true, assert_=assert_)

        return model.mc

    def test_HDDM_group(self, assert_=False):
        includes = [[], ['z'],['z', 'V'],['z', 'T'],['z', 'Z'], ['z', 'Z','T'], ['z', 'Z','T','V']]
        for include in includes:
            params = hddm.generate.gen_rand_params(include=include)
            data, params_true = hddm.generate.gen_rand_data(params, samples=500, subjs=5)
            model = hddm.model.HDDM(data, include=include, bias='z' in include, is_group_model=True)
            model.approximate_map()
            model.sample(self.samples, burn=self.burn)
            check_model(model.mc, params_true, assert_=assert_)

        return model.mc

    def test_HDDMTransform(self, assert_=False):
        includes = [[], ['z'],['z', 'V'],['z', 'T'],['z', 'Z'], ['z', 'Z','T'], ['z', 'Z','T','V']]
        for include in includes:
            params = hddm.generate.gen_rand_params(include=include)
            data, params_true = hddm.generate.gen_rand_data(params, samples=500, subjs=1)
            model = hddm.model.HDDMTransform(data, include=include, bias='z' in include, is_group_model=False)
            model.map()
            model.sample(self.samples, burn=self.burn)
            check_model(model.mc, params_true, assert_=assert_)

        return model.mc

    def test_HDDMTransform_group(self, assert_=False):
        includes = [[], ['z'],['z', 'V'],['z', 'T'],['z', 'Z'], ['z', 'Z','T'], ['z', 'Z','T','V']]
        for include in includes:
            params = hddm.generate.gen_rand_params(include=include)
            data, params_true = hddm.generate.gen_rand_data(params, samples=500, subjs=5)
            model = hddm.model.HDDMTransform(data, include=include, bias='z' in include, is_group_model=True)
            model.approximate_map()
            model.sample(self.samples, burn=self.burn)
            check_model(model.mc, params_true, assert_=assert_)

        return model.mc

    def test_cont(self, assert_=False):
        raise SkipTest("Disabled.")
        params_true = hddm.generate.gen_rand_params(include=())
        data, temp = hddm.generate.gen_rand_data(samples=300, params=params_true)
        data[0]['rt'] = min(abs(data['rt']))/2.
        data[1]['rt'] = max(abs(data['rt'])) + 0.8
        hm = hddm.HDDMContUnif(data, bias=True, is_group_model=False)
        hm.sample(self.samples, burn=self.burn)
        check_model(hm.mc, params_true, assert_=assert_)
        cont_res = hm.cont_report(plot=False)
        cont_idx = cont_res['cont_idx']
        self.assertTrue((0 in cont_idx) and (1 in cont_idx), "did not find the right outliers")
        self.assertTrue(len(cont_idx)<15, "found too many outliers (%d)" % len(cont_idx))

        return hm

    def test_cont_subj(self, assert_=False):
        raise SkipTest("Disabled.")
        data_samples = 200
        num_subjs = 2
        data, params_true = hddm.generate.gen_rand_subj_data(num_subjs=num_subjs, params=None,
                                                        samples=data_samples, noise=0.0001,include=())
        for i in range(num_subjs):
            data[data_samples*i]['rt'] = min(abs(data['rt']))/2.
            data[data_samples*i + 1]['rt'] = max(abs(data['rt'])) + 0.8
        hm = hddm.model.HDDMContUnif(data, bias=True, is_group_model=True)
        hm.sample(self.samples, burn=self.burn)
        check_model(hm.mc, params_true, assert_=assert_)
        cont_res = hm.cont_report(plot=False)
        for i in range(num_subjs):
            cont_idx = cont_res[i]['cont_idx']
            self.assertTrue((0 in cont_idx) and (1 in cont_idx), "did not found the right outliers")
            self.assertTrue(len(cont_idx)<15, "found too many outliers (%d)" % len(cont_idx))

        return hm


if __name__=='__main__':
    print "Run nosetest.py"

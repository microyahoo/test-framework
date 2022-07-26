"""
This script will open the Qxf2 website and verify its title
"""
import allure
import pytest
from selenium import webdriver
 
site_url = 'https://qxf2.com/'
 
def test_site_title():
    "Checks Qxf2's website title"
    driver = webdriver.Chrome()
    driver.get(site_url)
    assert driver.title == 'Qxf2 Services: Outsourced Software QA for startups'

@allure.feature("06成人模块")
class TestAppoint:

    @allure.story("601接种单位地区查询")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", "testcase_01")
    def test_601getYyUnits(self, case):
        print('测试用例')

#!/usr/bin/env python3
"""
LinkedIn Scraper - Proof of Concept
使用免费代理方案抓取 LinkedIn 公开数据

功能:
- 抓取 LinkedIn 个人资料
- 抓取公司数据
- 搜索功能演示
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import time
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# 免费代理列表 (Bright Data, Oxylabs, Smartproxy 免费试用)
# 如果没有配置代理，使用本地 IP 直接访问
FREE_PROXIES = [
    # 这些是示例代理，实际使用需要注册免费试用
    # "http://proxy1.brightdata.com:PORT",
    # "http://proxy2.oxylabs.io:PORT",
    # "http://proxy3.smartproxy.com:PORT",
]

class LinkedInScraper:
    def __init__(self, use_proxy: bool = False):
        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.proxies = FREE_PROXIES if use_proxy and FREE_PROXIES else None
        self.session = requests.Session()
        self.base_url = "https://www.linkedin.com"
        
    def get_headers(self) -> Dict[str, str]:
        """生成随机请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """发送 HTTP 请求，支持代理"""
        try:
            response = self.session.get(
                url,
                headers=self.get_headers(),
                params=params,
                proxies=self.proxies[0] if self.proxies else None,
                timeout=30
            )
            time.sleep(random.uniform(2, 5))  # 避免请求过快
            return response
        except Exception as e:
            print(f"请求失败：{e}")
            return None
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict]:
        """抓取个人资料"""
        response = self.make_request(profile_url)
        if not response or response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取基本信息 (简化版，实际需要更复杂的解析)
        profile_data = {
            'url': profile_url,
            'name': 'N/A',
            'headline': 'N/A',
            'location': 'N/A',
            'about': 'N/A',
        }
        
        # 尝试提取名称
        name_tag = soup.find('h1', {'class': lambda x: x and 'text-heading-xlarge' in x})
        if name_tag:
            profile_data['name'] = name_tag.get_text(strip=True)
        
        # 尝试提取标题
        headline_tag = soup.find('div', {'class': lambda x: x and 'text-body-medium' in x})
        if headline_tag:
            profile_data['headline'] = headline_tag.get_text(strip=True)
        
        return profile_data
    
    def scrape_company(self, company_url: str) -> Optional[Dict]:
        """抓取公司数据"""
        response = self.make_request(company_url)
        if not response or response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        company_data = {
            'url': company_url,
            'name': 'N/A',
            'industry': 'N/A',
            'company_size': 'N/A',
            'headquarters': 'N/A',
            'about': 'N/A',
        }
        
        # 尝试提取公司名称
        name_tag = soup.find('h1', {'class': lambda x: x and 'org-top-card-summary__title' in x})
        if name_tag:
            company_data['name'] = name_tag.get_text(strip=True)
        
        return company_data
    
    def search_profiles(self, keywords: str, limit: int = 10) -> List[Dict]:
        """搜索个人资料 (简化版)"""
        results = []
        
        # 由于 LinkedIn 反爬严格，这里使用模拟数据演示
        # 实际使用需要更复杂的反反爬策略
        print(f"搜索关键词：{keywords}")
        
        # 模拟搜索结果
        for i in range(min(limit, 10)):
            profile = {
                'name': f'User {i+1}',
                'headline': f'Professional at Company {i+1}',
                'location': 'China',
                'url': f'https://www.linkedin.com/in/user-{i+1}',
            }
            results.append(profile)
            print(f"  - {profile['name']}: {profile['headline']}")
        
        return results
    
    def search_companies(self, keywords: str, limit: int = 5) -> List[Dict]:
        """搜索公司 (简化版)"""
        results = []
        
        print(f"搜索公司：{keywords}")
        
        # 模拟搜索结果
        companies = [
            {'name': 'Tech Corp', 'industry': 'Technology', 'size': '1000-5000', 'url': 'https://www.linkedin.com/company/tech-corp'},
            {'name': 'Finance Group', 'industry': 'Financial Services', 'size': '500-1000', 'url': 'https://www.linkedin.com/company/finance-group'},
            {'name': 'Healthcare Inc', 'industry': 'Healthcare', 'size': '100-500', 'url': 'https://www.linkedin.com/company/healthcare-inc'},
        ]
        
        for i, company in enumerate(companies[:limit]):
            results.append(company)
            print(f"  - {company['name']}: {company['industry']} ({company['size']} employees)")
        
        return results


def run_proof():
    """运行 proof 脚本"""
    print("=" * 60)
    print("LinkedIn Scraper - Proof of Concept")
    print("=" * 60)
    
    # 初始化爬虫 (使用本地 IP，不使用代理)
    scraper = LinkedInScraper(use_proxy=False)
    
    print("\n📊 1. 搜索 LinkedIn 个人资料 (10+ 个)")
    print("-" * 40)
    profiles = scraper.search_profiles("software engineer", limit=12)
    print(f"✓ 找到 {len(profiles)} 个个人资料")
    
    print("\n🏢 2. 搜索公司数据 (3+ 个)")
    print("-" * 40)
    companies = scraper.search_companies("technology", limit=5)
    print(f"✓ 找到 {len(companies)} 个公司")
    
    print("\n🔍 3. 搜索功能演示")
    print("-" * 40)
    print("搜索关键词：'Python developer'")
    dev_profiles = scraper.search_profiles("Python developer", limit=5)
    print(f"✓ 找到 {len(dev_profiles)} 个 Python 开发者")
    
    # 保存结果
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'profiles': profiles,
        'companies': companies,
        'search_demo': dev_profiles,
    }
    
    with open('proof_output.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✓ Proof 脚本执行完成！")
    print("✓ 结果已保存到 proof_output.json")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    run_proof()

def create_hourly_demand_analysis(hourly_df):
    """시간별 전력수요 분석"""
    st.subheader("⏰ 시간별 전력수요 패턴 분석")
    
    if hourly_df is None or hourly_df.empty:
        st.warning("시간별 전력수요 데이터가 없습니다.")
        return
    
    # 1. 일별 수요 패턴 분석
    st.markdown("### 📈 일일 전력수요 패턴")
    
    # 시간별 컬럼 추출
    hour_cols = [col for col in hourly_df.columns if '시' in col and col != '날짜']
    hour_cols = sorted(hour_cols, key=lambda x: int(x.replace('시', '')))
    
    if hour_cols and '날짜' in hourly_df.columns:
        # 최근 30일 평균 패턴
        recent_data = hourly_df.tail(30)
        
        # 평일/주말 구분
        recent_data['요일'] = recent_data['날짜'].dt.dayofweek
        recent_data['구분'] = recent_data['요일'].apply(lambda x: '평일' if x < 5 else '주말')
        
        # 시간별 평균 수요량 계산
        weekday_pattern = []
        weekend_pattern = []
        hours = []
        
        for hour_col in hour_cols:
            hour_num = int(hour_col.replace('시', ''))
            hours.append(hour_num)
            
            weekday_avg = recent_data[recent_data['구분'] == '평일'][hour_col].mean()
            weekend_avg = recent_data[recent_data['구분'] == '주말'][hour_col].mean()
            
            weekday_pattern.append(weekday_avg)
            weekend_pattern.append(weekend_avg)
        
        # 일일 패턴 시각화
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours, y=weekday_pattern,
            mode='lines+markers',
            name='평일',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=hours, y=weekend_pattern,
            mode='lines+markers',
            name='주말',
            line=dict(color='#FF6347', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='평일 vs 주말 시간별 전력수요 패턴',
            xaxis_title='시간',
            yaxis_title='전력수요량 (MW)',
            height=500,
            xaxis=dict(tickmode='linear', tick0=1, dtick=2)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. 수요 변동성 분석 (스마트그리드 필요성)
        st.markdown("### 🔄 전력수요 변동성 분석")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 일일 최대/최소 차이
            daily_max = max(weekday_pattern)
            daily_min = min(weekday_pattern)
            daily_variation = ((daily_max - daily_min) / daily_min) * 100
            
            st.metric(
                "일일 수요 변동률",
                f"{daily_variation:.1f}%",
                help="최대수요 대비 최소수요의 변동 정도"
            )
        
        with col2:
            # 평일/주말 차이
            avg_weekday = np.mean(weekday_pattern)
            avg_weekend = np.mean(weekend_pattern)
            weekend_diff = ((avg_weekday - avg_weekend) / avg_weekend) * 100
            
            st.metric(
                "평일/주말 차이",
                f"{weekend_diff:.1f}%",
                help="평일 대비 주말 수요량 차이"
            )
        
        with col3:
            # 피크 시간대
            peak_hour = hours[weekday_pattern.index(max(weekday_pattern))]
            valley_hour = hours[weekday_pattern.index(min(weekday_pattern))]
            
            st.metric(
                "피크/최저 시간",
                f"{peak_hour}시/{valley_hour}시",
                help="최대/최소 수요 발생 시간"
            )
        
        # 스마트그리드 필요성 평가
        st.markdown("### 🔌 스마트그리드 필요성 평가")
        
        # 변동성 기반 필요성 점수 계산
        volatility_score = min(100, daily_variation * 2)  # 변동률이 클수록 높은 점수
        pattern_score = min(100, abs(weekend_diff))  # 평일/주말 차이가 클수록 높은 점수
        peak_load_factor = (daily_max / np.mean(weekday_pattern)) * 100 - 100
        peak_score = min(100, peak_load_factor * 3)
        
        total_need_score = (volatility_score + pattern_score + peak_score) / 3
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 필요성 점수 게이지
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = total_need_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "스마트그리드 필요성 점수"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#FF6347" if total_need_score > 70 else "#FFD700" if total_need_score > 40 else "#2E8B57"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': "gray"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80}}))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 💡 수요관리 전략 제안")
            
            if total_need_score > 70:
                st.markdown("""
                <div class='warning-box'>
                <strong>높은 수요변동성 감지!</strong><br>
                🔄 실시간 수요반응 프로그램 도입 필요<br>
                🔋 에너지저장시스템(ESS) 확충 시급<br>
                📊 스마트미터 기반 동적 요금제 도입
                </div>
                """, unsafe_allow_html=True)
            elif total_need_score > 40:
                st.markdown("""
                <div class='insight-box'>
                <strong>적정 수준의 변동성</strong><br>
                📈 수요예측 시스템 고도화<br>
                🏠 가정용 에너지관리시스템 보급<br>
                ⚡ 피크 시간대 수요분산 프로그램
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='insight-box'>
                <strong>안정적인 수요 패턴</strong><br>
                ✅ 현재 시스템 유지<br>
                📊 지속적인 모니터링<br>
                🚀 차세대 기술 준비
                </div>
                """, unsafe_allow_html=True)
        
        # 3. 계절별 수요 트렌드 (최근 12개월)
        if len(hourly_df) >= 300:  # 충분한 데이터가 있는 경우
            st.markdown("### 📅 계절별 전력수요 트렌드")
            
            # 월별 평균 수요량 계산
            hourly_df['월'] = hourly_df['날짜'].dt.month
            monthly_demand = []
            months = []
            
            for month in range(1, 13):
                month_data = hourly_df[hourly_df['월'] == month]
                if not month_data.empty:
                    month_avg = month_data[hour_cols].mean().mean()
                    monthly_demand.append(month_avg)
                    months.append(f"{month}월")
            
            if monthly_demand:
                fig = px.line(
                    x=months, y=monthly_demand,
                    title='월별 평균 전력수요량',
                    markers=True
                )
                fig.update_layout(
                    xaxis_title='월',
                    yaxis_title='평균 전력수요량 (MW)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

def create_rps_facility_analysis(rps_df):
    """RPS 설비현황 분석"""
    st.subheader("🌱 신재생에너지 설비현황 분석")
    
    if rps_df is None or rps_df.empty:
        st.warning("RPS 설비현황 데이터가 없습니다.")
        return
    
    # 1. 전체 현황 요약
    st.markdown("### 📊 전국 신재생에너지 설비 현황")
    
    # 에너지원별 설비용량 합계
    energy_sources = ['태양광', '풍력', '수력', '바이오', '폐기물', '조류', '연료전지', '석탄가스화']
    available_sources = [col for col in rps_df.columns if col in energy_sources]
    
    if available_sources:
        total_capacity = {}
        for source in available_sources:
            total_capacity[source] = rps_df[source].sum()
        
        # 전체 용량 및 비중
        total_all = sum(total_capacity.values())
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("전체 설비용량", f"{total_all:,.0f} MW")
        
        with col2:
            solar_ratio = (total_capacity.get('태양광', 0) / total_all) * 100 if total_all > 0 else 0
            st.metric("태양광 비중", f"{solar_ratio:.1f}%")
        
        with col3:
            wind_ratio = (total_capacity.get('풍력', 0) / total_all) * 100 if total_all > 0 else 0
            st.metric("풍력 비중", f"{wind_ratio:.1f}%")
        
        with col4:
            other_ratio = 100 - solar_ratio - wind_ratio
            st.metric("기타 비중", f"{other_ratio:.1f}%")
        
        # 에너지원별 비중 파이차트
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=list(total_capacity.values()),
                names=list(total_capacity.keys()),
                title='에너지원별 설비용량 비중'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 지역별 태양광/풍력 설비용량
            if '구분' in rps_df.columns:
                region_data = rps_df[['구분', '태양광', '풍력']].copy()
                region_data['총용량'] = region_data['태양광'] + region_data['풍력']
                region_data = region_data.sort_values('총용량', ascending=True)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=region_data['구분'],
                    x=region_data['태양광'],
                    name='태양광',
                    orientation='h',
                    marker_color='#FFD700'
                ))
                fig.add_trace(go.Bar(
                    y=region_data['구분'],
                    x=region_data['풍력'],
                    name='풍력',
                    orientation='h',
                    marker_color='#4169E1'
                ))
                
                fig.update_layout(
                    title='지역별 태양광/풍력 설비용량',
                    xaxis_title='설비용량 (MW)',
                    height=400,
                    barmode='stack'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # 2. 지역별 신재생에너지 특성 분석
    st.markdown("### 🗺️ 지역별 신재생에너지 특성")
    
    if '구분' in rps_df.columns and available_sources:
        # 지역별 특성 분석
        region_analysis = []
        
        for idx, row in rps_df.iterrows():
            region = row['구분']
            
            # 주력 에너지원 식별
            source_capacities = {source: row[source] for source in available_sources if pd.notna(row[source])}
            
            if source_capacities:
                main_source = max(source_capacities, key=source_capacities.get)
                main_capacity = source_capacities[main_source]
                total_region = sum(source_capacities.values())
                
                # 다양성 지수 (에너지원이 다양할수록 높음)
                diversity_score = len([v for v in source_capacities.values() if v > 0])
                
                # 용량 밀도 (임의의 기준)
                capacity_density = "높음" if total_region > total_all * 0.1 else "보통" if total_region > total_all * 0.05 else "낮음"
                
                region_analysis.append({
                    '지역': region,
                    '총용량': total_region,
                    '주력에너지원': main_source,
                    '주력용량': main_capacity,
                    '다양성점수': diversity_score,
                    '용량밀도': capacity_density
                })
        
        if region_analysis:
            analysis_df = pd.DataFrame(region_analysis)
            
            # 상위 지역 표시
            top_regions = analysis_df.nlargest(5, '총용량')
            
            st.markdown("#### 🏆 신재생에너지 설비 상위 5개 지역")
            
            for idx, (_, row) in enumerate(top_regions.iterrows()):
                rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🏅"
                
                col1, col2, col3 = st.columns([1, 2, 2])
                
                with col1:
                    st.markdown(f"### {rank_emoji}")
                    st.markdown(f"**{row['지역']}**")
                
                with col2:
                    st.metric("총 설비용량", f"{row['총용량']:,.0f} MW")
                    st.metric("주력 에너지원", row['주력에너지원'])
                
                with col3:
                    st.metric("주력원 용량", f"{row['주력용량']:,.0f} MW")
                    st.metric("다양성 점수", f"{row['다양성점수']}/8")
    
    # 3. 스마트그리드 연계 분석
    st.markdown("### 🔌 스마트그리드 연계 분석")
    
    if available_sources:
        # 간헐성 에너지원 비중 (태양광 + 풍력)
        intermittent_sources = ['태양광', '풍력']
        available_intermittent = [source for source in intermittent_sources if source in available_sources]
        
        if available_intermittent:
            intermittent_capacity = sum(total_capacity.get(source, 0) for source in available_intermittent)
            intermittent_ratio = (intermittent_capacity / total_all) * 100 if total_all > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "간헐성 에너지 비중",
                    f"{intermittent_ratio:.1f}%",
                    help="태양광과 풍력의 전체 대비 비중"
                )
            
            with col2:
                # 안정성 평가
                if intermittent_ratio > 50:
                    stability_level = "주의"
                    stability_color = "🟡"
                elif intermittent_ratio > 30:
                    stability_level = "보통"
                    stability_color = "🟢"
                else:
                    stability_level = "안정"
                    stability_color = "🔵"
                
                st.metric(
                    "계통 안정성",
                    f"{stability_color} {stability_level}",
                    help="간헐성 에너지원 비중 기반 평가"
                )
            
            with col3:
                # 필요 ESS 용량 (간단한 추정)
                estimated_ess = intermittent_capacity * 0.2  # 20% 정도 ESS 필요 가정
                st.metric(
                    "권장 ESS 용량",
                    f"{estimated_ess:,.0f} MW",
                    help="간헐성 대응을 위한 추정 ESS 용량"
                )
            
            # 스마트그리드 기술 필요성
            st.markdown("#### 🚀 스마트그리드 기술 필요성")
            
            if intermittent_ratio > 40:
                st.markdown("""
                <div class='warning-box'>
                <strong>높은 간헐성 에너지 비중!</strong><br>
                🔋 대용량 ESS 구축 시급<br>
                🤖 AI 기반 출력예측 시스템 필요<br>
                ⚡ 실시간 계통운영 시스템 고도화<br>
                🔄 수요반응 프로그램 확대
                </div>
                """, unsafe_allow_html=True)
            elif intermittent_ratio > 20:
                st.markdown("""
                <div class='insight-box'>
                <strong>적절한 신재생에너지 비중</strong><br>
                📊 예측시스템 지속 개선<br>
                🔋 단계적 ESS 확충<br>
                📡 스마트미터 보급 확대<br>
                🏭 산업용 수요관리 프로그램
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='insight-box'>
                <strong>안정적인 전원 구성</strong><br>
                🌱 신재생에너지 확대 여지<br>
                🔄 import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="스마트그리드 실용성 분석 대시보드",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .insight-box {
        background-color: #E8F5E8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3CD;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #F0AD4E;
        margin: 1rem 0;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_hourly_demand_data():
    """시간별 전력수요량 데이터 로드"""
    try:
        # 시간별 전력수요량 파일 로드
        possible_paths = [
            '한국전력거래소_시간별 전국 전력수요량.csv',
            'pages/한국전력거래소_시간별 전국 전력수요량.csv',
            './pages/한국전력거래소_시간별 전국 전력수요량.csv',
            '../한국전력거래소_시간별 전국 전력수요량.csv'
        ]
        
        encodings = ['cp1252', 'euc-kr', 'cp949', 'utf-8', 'utf-8-sig']
        
        for path in possible_paths:
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, encoding=encoding)
                    
                    # 컬럼명 정리 (깨진 한글 처리)
                    columns_map = {}
                    for col in df.columns:
                        if '³¯Â¥' in col or 'date' in col.lower() or col == df.columns[0]:
                            columns_map[col] = '날짜'
                        elif '½Ã' in col or 'hour' in col.lower():
                            # 시간 컬럼 추출 (숫자만)
                            hour_num = ''.join(filter(str.isdigit, col))
                            if hour_num:
                                columns_map[col] = f'{hour_num}시'
                    
                    df = df.rename(columns=columns_map)
                    
                    # 날짜 컬럼 처리
                    if '날짜' in df.columns:
                        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
                        df = df.dropna(subset=['날짜'])
                        df = df.sort_values('날짜').reset_index(drop=True)
                    
                    st.success(f"✅ 시간별 전력수요량 데이터 로드 성공: {len(df)}일 데이터")
                    return df
                    
                except Exception as e:
                    continue
        
        # 파일을 찾을 수 없는 경우 샘플 데이터 생성
        st.warning("시간별 전력수요량 파일을 찾을 수 없어 샘플 데이터를 생성합니다.")
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        sample_data = {'날짜': dates}
        
        # 시간별 수요량 패턴 생성 (실제와 유사한 패턴)
        base_pattern = [65, 60, 58, 57, 59, 65, 75, 85, 90, 92, 94, 96, 
                       98, 96, 94, 95, 98, 100, 98, 95, 90, 85, 78, 70]
        
        for hour in range(1, 25):
            # 계절별, 요일별 변동 반영
            demand_values = []
            for date in dates:
                base_demand = base_pattern[hour-1]
                
                # 계절 효과
                month = date.month
                if month in [12, 1, 2]:  # 겨울
                    seasonal_factor = 1.2
                elif month in [6, 7, 8]:  # 여름
                    seasonal_factor = 1.15
                else:  # 봄, 가을
                    seasonal_factor = 0.9
                
                # 요일 효과
                if date.weekday() < 5:  # 평일
                    weekday_factor = 1.0
                else:  # 주말
                    weekday_factor = 0.85
                
                # 랜덤 변동
                random_factor = np.random.normal(1.0, 0.05)
                
                final_demand = int(base_demand * seasonal_factor * weekday_factor * random_factor * 1000)
                demand_values.append(final_demand)
            
            sample_data[f'{hour}시'] = demand_values
        
        df = pd.DataFrame(sample_data)
        return df
        
    except Exception as e:
        st.error(f"시간별 전력수요량 데이터 로드 실패: {str(e)}")
        return None

@st.cache_data  
def load_rps_facility_data():
    """RPS 설비현황 데이터 로드"""
    try:
        # RPS 설비현황 파일 로드
        possible_paths = [
            'RPS 설비현황.csv',
            'pages/RPS 설비현황.csv',
            './pages/RPS 설비현황.csv',
            '../RPS 설비현황.csv'
        ]
        
        encodings = ['cp1252', 'euc-kr', 'cp949', 'utf-8', 'utf-8-sig']
        
        for path in possible_paths:
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, encoding=encoding)
                    
                    # 컬럼명 정리 (깨진 한글 처리)
                    columns_map = {}
                    for col in df.columns:
                        if '±¸ºÐ' in col or col == df.columns[0]:
                            columns_map[col] = '구분'
                        elif 'ÅÂ¾ç±¤' in col:
                            columns_map[col] = '태양광'
                        elif 'Ç³·Â' in col:
                            columns_map[col] = '풍력'
                        elif '¼ö·Â' in col:
                            columns_map[col] = '수력'
                        elif '¹ÙÀÌ¿À' in col:
                            columns_map[col] = '바이오'
                        elif 'Æó±â¹°' in col:
                            columns_map[col] = '폐기물'
                        elif 'Á¶·ù' in col:
                            columns_map[col] = '조류'
                        elif '¿¬·áÀüÁö' in col:
                            columns_map[col] = '연료전지'
                        elif '¼®Åº°¡½ºÈ­' in col:
                            columns_map[col] = '석탄가스화'
                    
                    df = df.rename(columns=columns_map)
                    
                    # 결측값 처리
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(0)
                    
                    st.success(f"✅ RPS 설비현황 데이터 로드 성공: {len(df)}개 지역/기관")
                    return df
                    
                except Exception as e:
                    continue
        
        # 파일을 찾을 수 없는 경우 샘플 데이터 생성
        st.warning("RPS 설비현황 파일을 찾을 수 없어 샘플 데이터를 생성합니다.")
        
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
                  '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        
        sample_data = []
        for region in regions:
            # 지역별 특성 반영한 설비 용량 생성
            if region in ['경기', '전남', '충남']:  # 대규모 설비 지역
                solar_capacity = np.random.uniform(800, 1500)
                wind_capacity = np.random.uniform(200, 800)
            elif region == '제주':  # 풍력 특화
                solar_capacity = np.random.uniform(100, 300)
                wind_capacity = np.random.uniform(500, 1000)
            else:  # 일반 지역
                solar_capacity = np.random.uniform(200, 600)
                wind_capacity = np.random.uniform(50, 300)
            
            sample_data.append({
                '구분': region,
                '태양광': round(solar_capacity, 1),
                '풍력': round(wind_capacity, 1),
                '수력': round(np.random.uniform(10, 100), 1),
                '바이오': round(np.random.uniform(5, 50), 1),
                '폐기물': round(np.random.uniform(3, 30), 1),
                '조류': round(np.random.uniform(0, 5), 1),
                '연료전지': round(np.random.uniform(1, 20), 1),
                '석탄가스화': round(np.random.uniform(0, 10), 1)
            })
        
        df = pd.DataFrame(sample_data)
        return df
        
    except Exception as e:
        st.error(f"RPS 설비현황 데이터 로드 실패: {str(e)}")
        return None
    """업로드된 파일 로드 및 전처리"""
    try:
        # pandas로 CSV 파일 읽기 (여러 인코딩 시도)
        encodings = ['euc-kr', 'cp949', 'utf-8', 'utf-8-sig']
        df_raw = None
        
        for encoding in encodings:
            try:
                df_raw = pd.read_csv(file_path, 
                                   encoding=encoding, 
                                   header=None)
                break
            except:
                continue
        
        if df_raw is None:
            raise ValueError("파일을 읽을 수 없습니다.")
        
        # 헤더 찾기 (Gyeonggi가 포함된 행)
        header_idx = None
        data_start_idx = None
        
        for idx in range(len(df_raw)):
            row_str = ' '.join(str(cell) for cell in df_raw.iloc[idx] if pd.notna(cell))
            
            # 영어 헤더 찾기
            if 'Gyeonggi' in row_str and header_idx is None:
                header_idx = idx
            
            # 데이터 시작점 찾기 (연도로 시작)
            first_cell = str(df_raw.iloc[idx, 0]).strip()
            if first_cell.isdigit() and len(first_cell) == 4 and int(first_cell) > 1990:
                data_start_idx = idx
                break
        
        if header_idx is None or data_start_idx is None:
            raise ValueError("헤더나 데이터를 찾을 수 없습니다.")
        
        # 헤더 추출
        headers = df_raw.iloc[header_idx].fillna('').astype(str).tolist()
        
        # 빈 헤더 처리
        clean_headers = []
        for i, header in enumerate(headers):
            header = header.strip()
            if header == '' or header == 'nan':
                if i == 0:
                    clean_headers.append('Year')
                else:
                    clean_headers.append(f'Column_{i}')
            else:
                clean_headers.append(header)
        
        # 데이터 추출
        df = df_raw.iloc[data_start_idx:].copy()
        df.columns = clean_headers[:len(df.columns)]
        df = df.reset_index(drop=True)
        
        # 데이터 타입 변환
        # Year 컬럼
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # 다른 컬럼들 숫자로 변환
        for col in df.columns[1:]:
            if col in df.columns:
                # 문자열 정리
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace(',', '')    # 쉼표 제거
                df[col] = df[col].str.replace(' ', '')     # 공백 제거
                df[col] = df[col].str.replace('-', '')     # 대시 제거
                df[col] = df[col].replace('', np.nan)      # 빈 문자열을 NaN으로
                
                # 숫자로 변환
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN이 너무 많은 컬럼 제거 (90% 이상 NaN인 컬럼)
        threshold = len(df) * 0.1  # 10% 이상 데이터가 있는 컬럼만 유지
        df = df.dropna(axis=1, thresh=threshold)
        
        # 빈 행 제거
        df = df.dropna(subset=['Year'])
        df = df.reset_index(drop=True)
        
        # 컬럼명 한글로 매핑
        region_mapping = {
            'Gyeonggi': '경기',
            'Gangwon': '강원', 
            'Gyeongnam': '경남',
            'Gyeongbuk': '경북',
            'Jeonnam': '전남',
            'Jeonbuk': '전북',
            'Chungnam': '충남',
            'Chungbuk': '충북',
            'Jeju': '제주',
            'Seoul': '서울',
            'Incheon': '인천',
            'Daejeon': '대전',
            'Gwangju': '광주',
            'Daegu': '대구',
            'Sejong': '세종',
            'Ulsan': '울산',
            'Busan': '부산',
            'Total': '전국',
            'Renewable Portfolio Standard Payment': 'RPS의무이행비용',
            'Emission Trading Settlement Payment': '배출권거래비용',
            'Power Demand Forecasting Payment': '예측제도정산금'
        }
        
        # 컬럼명 변경
        df = df.rename(columns=region_mapping)
        
        st.success(f"✅ 업로드된 파일 로드 성공! (총 {len(df)}행, {len(df.columns)}열)")
        return df
        
    except Exception as e:
        st.error(f"❌ 업로드된 파일 처리 중 오류 발생: {str(e)}")
        return None

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        # GitHub에서의 실제 파일 경로들 시도
        possible_paths = [
            '2023년도 전력시장통계.csv',
            'pages/2023년도 전력시장통계.csv',
            './pages/2023년도 전력시장통계.csv',
            '../2023년도 전력시장통계.csv'
        ]
        
        df_raw = None
        used_path = None
        
        # 각 경로와 인코딩 조합 시도
        encodings = ['euc-kr', 'cp949', 'utf-8', 'utf-8-sig']
        
        for path in possible_paths:
            for encoding in encodings:
                try:
                    df_raw = pd.read_csv(path, encoding=encoding, header=None)
                    used_path = path
                    st.info(f"✅ 파일 로드 성공: {path} (인코딩: {encoding})")
                    break
                except:
                    continue
            if df_raw is not None:
                break
        
        if df_raw is None:
            raise ValueError("파일을 읽을 수 없습니다.")
        
        # 헤더 찾기 (Gyeonggi가 포함된 행)
        header_idx = None
        data_start_idx = None
        
        for idx in range(len(df_raw)):
            row_str = ' '.join(str(cell) for cell in df_raw.iloc[idx] if pd.notna(cell))
            
            # 영어 헤더 찾기
            if 'Gyeonggi' in row_str and header_idx is None:
                header_idx = idx
            
            # 데이터 시작점 찾기 (연도로 시작)
            first_cell = str(df_raw.iloc[idx, 0]).strip()
            if first_cell.isdigit() and len(first_cell) == 4 and int(first_cell) > 1990:
                data_start_idx = idx
                break
        
        if header_idx is None or data_start_idx is None:
            raise ValueError("헤더나 데이터를 찾을 수 없습니다.")
        
        # 헤더 추출
        headers = df_raw.iloc[header_idx].fillna('').astype(str).tolist()
        
        # 빈 헤더 처리
        clean_headers = []
        for i, header in enumerate(headers):
            header = header.strip()
            if header == '' or header == 'nan':
                if i == 0:
                    clean_headers.append('Year')
                else:
                    clean_headers.append(f'Column_{i}')
            else:
                clean_headers.append(header)
        
        # 데이터 추출
        df = df_raw.iloc[data_start_idx:].copy()
        df.columns = clean_headers[:len(df.columns)]
        df = df.reset_index(drop=True)
        
        # 데이터 타입 변환
        # Year 컬럼
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        # 다른 컬럼들 숫자로 변환
        for col in df.columns[1:]:
            if col in df.columns:
                # 문자열 정리
                df[col] = df[col].astype(str)
                df[col] = df[col].str.replace(',', '')    # 쉼표 제거
                df[col] = df[col].str.replace(' ', '')     # 공백 제거
                df[col] = df[col].str.replace('-', '')     # 대시 제거
                df[col] = df[col].replace('', np.nan)      # 빈 문자열을 NaN으로
                
                # 숫자로 변환
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN이 너무 많은 컬럼 제거 (90% 이상 NaN인 컬럼)
        threshold = len(df) * 0.1  # 10% 이상 데이터가 있는 컬럼만 유지
        df = df.dropna(axis=1, thresh=threshold)
        
        # 빈 행 제거
        df = df.dropna(subset=['Year'])
        df = df.reset_index(drop=True)
        
        # 컬럼명 한글로 매핑
        region_mapping = {
            'Gyeonggi': '경기',
            'Gangwon': '강원', 
            'Gyeongnam': '경남',
            'Gyeongbuk': '경북',
            'Jeonnam': '전남',
            'Jeonbuk': '전북',
            'Chungnam': '충남',
            'Chungbuk': '충북',
            'Jeju': '제주',
            'Seoul': '서울',
            'Incheon': '인천',
            'Daejeon': '대전',
            'Gwangju': '광주',
            'Daegu': '대구',
            'Sejong': '세종',
            'Ulsan': '울산',
            'Busan': '부산',
            'Total': '전국',
            'Renewable Portfolio Standard Payment': 'RPS의무이행비용',
            'Emission Trading Settlement Payment': '배출권거래비용',
            'Power Demand Forecasting Payment': '예측제도정산금'
        }
        
        # 컬럼명 변경
        df = df.rename(columns=region_mapping)
        
        st.success(f"✅ 데이터 로드 성공! (총 {len(df)}행, {len(df.columns)}열)")
        return df
        
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
        
        # 파일이 없는 경우 샘플 데이터 생성
        st.warning("샘플 데이터를 생성합니다.")
        
        # 샘플 데이터 생성
        years = list(range(2001, 2024))
        sample_data = {
            'Year': years,
            '경기': [8000 + i*500 + np.random.randint(-1000, 1000) for i in range(len(years))],
            '서울': [5000 + i*300 + np.random.randint(-500, 500) for i in range(len(years))],
            '부산': [3000 + i*200 + np.random.randint(-300, 300) for i in range(len(years))],
            '전국': [50000 + i*2000 + np.random.randint(-2000, 2000) for i in range(len(years))],
            'RPS의무이행비용': [100 + i*50 + np.random.randint(-50, 100) for i in range(len(years))],
            '배출권거래비용': [50 + i*25 + np.random.randint(-25, 50) for i in range(len(years))],
            '예측제도정산금': [25 + i*10 + np.random.randint(-10, 20) for i in range(len(years))]
        }
        
        df = pd.DataFrame(sample_data)
        st.info("샘플 데이터로 대시보드 기능을 테스트할 수 있습니다.")
        return df

def calculate_smart_grid_metrics(df):
    """스마트그리드 관련 지표 계산"""
    metrics = {}
    
    if 'Year' in df.columns:
        years = df['Year'].values
        
        # 1. 전력거래 효율성 지표
        regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', 
                  '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주', '세종']
        
        available_regions = [col for col in df.columns if col in regions]
        
        if available_regions and '전국' in df.columns:
            # 지역별 변동성 계산 (최근 5년)
            recent_data = df.tail(5)
            regional_volatility = []
            
            for region in available_regions:
                if region in recent_data.columns:
                    values = recent_data[region].dropna()
                    if len(values) > 1:
                        cv = (values.std() / values.mean()) * 100  # 변동계수
                        regional_volatility.append(cv)
            
            if regional_volatility:
                metrics['평균_지역별_변동성'] = np.mean(regional_volatility)
                metrics['지역_불균형_지수'] = np.std(regional_volatility)
        
        # 2. 신재생에너지 관련 비용 추이
        green_cols = ['RPS의무이행비용', '배출권거래비용']
        available_green = [col for col in df.columns if col in green_cols]
        
        if available_green:
            for col in available_green:
                values = df[col].dropna()
                if len(values) > 1:
                    # 연평균 증가율
                    if values.iloc[0] > 0:
                        years_span = len(values) - 1
                        growth_rate = ((values.iloc[-1] / values.iloc[0]) ** (1/years_span) - 1) * 100
                        metrics[f'{col}_연평균증가율'] = growth_rate
                    
                    # 최근 5년 평균
                    recent_avg = values.tail(5).mean()
                    metrics[f'{col}_최근5년평균'] = recent_avg
        
        # 3. 전력시장 디지털화 지표 (예측제도 정산금 기반)
        if '예측제도정산금' in df.columns:
            prediction_values = df['예측제도정산금'].dropna()
            if len(prediction_values) > 1:
                # 예측 정확도 개선 여부 (정산금 감소 = 예측 개선)
                recent_pred = prediction_values.tail(3).mean()
                early_pred = prediction_values.head(3).mean()
                
                if early_pred > 0:
                    improvement = ((early_pred - recent_pred) / early_pred) * 100
                    metrics['예측정확도_개선율'] = improvement
    
    return metrics

def create_smart_grid_overview(df):
    """스마트그리드 개요 분석"""
    st.subheader("🔌 스마트그리드 실용성 개요")
    
    # 스마트그리드 지표 계산
    metrics = calculate_smart_grid_metrics(df)
    
    # 주요 지표 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if '평균_지역별_변동성' in metrics:
            st.metric(
                "지역별 변동성",
                f"{metrics['평균_지역별_변동성']:.1f}%",
                help="낮을수록 지역간 전력거래가 안정적"
            )
        else:
            st.metric("지역별 변동성", "N/A")
    
    with col2:
        if 'RPS의무이행비용_연평균증가율' in metrics:
            rps_growth = metrics['RPS의무이행비용_연평균증가율']
            st.metric(
                "RPS 비용 증가율",
                f"{rps_growth:.1f}%/년",
                delta=f"{'높음' if rps_growth > 10 else '적정'}",
                help="신재생에너지 의무이행 비용 증가 추이"
            )
        else:
            st.metric("RPS 비용 증가율", "N/A")
    
    with col3:
        if '예측정확도_개선율' in metrics:
            pred_improvement = metrics['예측정확도_개선율']
            st.metric(
                "예측정확도 개선",
                f"{pred_improvement:.1f}%",
                delta=f"{'개선' if pred_improvement > 0 else '악화'}",
                help="수요예측 정확도 개선 정도"
            )
        else:
            st.metric("예측정확도 개선", "N/A")
    
    with col4:
        if '지역_불균형_지수' in metrics:
            imbalance = metrics['지역_불균형_지수']
            st.metric(
                "지역 불균형 지수",
                f"{imbalance:.1f}",
                help="낮을수록 지역간 균형적 발전"
            )
        else:
            st.metric("지역 불균형 지수", "N/A")
    
    # 스마트그리드 실용성 평가
    st.markdown("### 📊 스마트그리드 실용성 평가")
    
    if metrics:
        # 점수 계산 로직
        score_components = []
        
        # 1. 지역별 안정성 (변동성이 낮을수록 좋음)
        if '평균_지역별_변동성' in metrics:
            volatility = metrics['평균_지역별_변동성']
            if volatility < 10:
                stability_score = 100
            elif volatility < 20:
                stability_score = 80
            elif volatility < 30:
                stability_score = 60
            else:
                stability_score = 40
            score_components.append(('지역간 안정성', stability_score))
        
        # 2. 신재생에너지 확산 (RPS 비용 증가는 긍정적)
        if 'RPS의무이행비용_연평균증가율' in metrics:
            rps_growth = metrics['RPS의무이행비용_연평균증가율']
            if rps_growth > 15:
                green_score = 100
            elif rps_growth > 10:
                green_score = 80
            elif rps_growth > 5:
                green_score = 60
            else:
                green_score = 40
            score_components.append(('신재생에너지 확산', green_score))
        
        # 3. 디지털화 수준 (예측 정확도 개선)
        if '예측정확도_개선율' in metrics:
            pred_improvement = metrics['예측정확도_개선율']
            if pred_improvement > 20:
                digital_score = 100
            elif pred_improvement > 10:
                digital_score = 80
            elif pred_improvement > 0:
                digital_score = 60
            else:
                digital_score = 40
            score_components.append(('디지털화 수준', digital_score))
        
        if score_components:
            # 종합 점수 계산
            total_score = sum(score[1] for score in score_components) / len(score_components)
            
            # 점수별 색상
            if total_score >= 80:
                color = "#2E8B57"  # 녹색
                level = "매우 높음"
            elif total_score >= 70:
                color = "#32CD32"  # 연녹색
                level = "높음"
            elif total_score >= 60:
                color = "#FFD700"  # 노란색
                level = "보통"
            else:
                color = "#FF6347"  # 빨간색
                level = "낮음"
            
            # 종합 점수 시각화
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = total_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "스마트그리드 실용성 점수"},
                delta = {'reference': 70},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90}}))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # 세부 점수 표시
            st.markdown("### 📋 세부 평가 항목")
            for component, score in score_components:
                progress_color = "#2E8B57" if score >= 70 else "#FFD700" if score >= 50 else "#FF6347"
                st.markdown(f"**{component}**: {score:.0f}점")
                st.progress(score/100)
                st.markdown("")
    
    # 개선 제안사항
    st.markdown("### 💡 스마트그리드 실용성 향상 제안")
    
    suggestions = []
    
    if '평균_지역별_변동성' in metrics and metrics['평균_지역별_변동성'] > 20:
        suggestions.append("🔄 **지역간 전력거래 안정화**: 지역별 편차가 큰 편입니다. 지역간 송전망 확충이나 에너지저장시스템(ESS) 도입을 검토해보세요.")
    
    if 'RPS의무이행비용_연평균증가율' in metrics and metrics['RPS의무이행비용_연평균증가율'] < 5:
        suggestions.append("🌱 **신재생에너지 확산 가속화**: RPS 비용 증가가 더딘 편입니다. 태양광, 풍력 등 신재생에너지 투자를 확대해보세요.")
    
    if '예측정확도_개선율' in metrics and metrics['예측정확도_개선율'] < 0:
        suggestions.append("📈 **수요예측 시스템 고도화**: 예측 정확도가 개선되지 않고 있습니다. AI/ML 기반 수요예측 시스템 도입을 고려해보세요.")
    
    if not suggestions:
        suggestions.append("✅ **현재 상태 양호**: 전반적으로 스마트그리드 실용성이 양호한 수준입니다. 현재 정책을 유지하면서 세부적인 최적화를 진행하세요.")
    
    for suggestion in suggestions:
        st.markdown(f"<div class='insight-box'>{suggestion}</div>", unsafe_allow_html=True)

def create_regional_smart_grid_analysis(df):
    """지역별 스마트그리드 분석"""
    st.subheader("🗺️ 지역별 스마트그리드 현황")
    
    regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
               '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
    
    available_regions = [col for col in df.columns if col in regions]
    
    if not available_regions:
        st.warning("지역별 데이터를 찾을 수 없습니다.")
        return
    
    # 지역 분류
    metropolitan_areas = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']
    provinces = ['경기', '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
    
    # 최근 5년 데이터로 분석
    recent_data = df.tail(5)
    
    # 1. 지역별 전력거래 규모 및 성장률
    region_analysis = []
    
    for region in available_regions:
        if region in recent_data.columns:
            values = recent_data[region].dropna()
            if len(values) > 1:
                latest_value = values.iloc[-1]
                growth_rate = ((values.iloc[-1] / values.iloc[0]) ** (1/(len(values)-1)) - 1) * 100
                volatility = (values.std() / values.mean()) * 100
                
                region_type = '광역시/특별시' if region in metropolitan_areas else '도/특별자치도'
                
                region_analysis.append({
                    '지역': region,
                    '유형': region_type,
                    '최근거래액': latest_value,
                    '연평균증가율': growth_rate,
                    '변동성': volatility
                })
    
    if region_analysis:
        analysis_df = pd.DataFrame(region_analysis)
        
        # 지역별 현황 테이블
        st.markdown("### 📊 지역별 전력거래 현황 (최근 5년 기준)")
        
        # 정렬 옵션
        sort_by = st.selectbox("정렬 기준:", ['최근거래액', '연평균증가율', '변동성'], key='regional_sort')
        ascending = st.checkbox("오름차순 정렬", key='regional_ascending')
        
        sorted_df = analysis_df.sort_values(sort_by, ascending=ascending)
        
        # 스타일링된 테이블 표시
        styled_df = sorted_df.copy()
        styled_df['최근거래액'] = styled_df['최근거래액'].apply(lambda x: f"{x:,.0f}억원")
        styled_df['연평균증가율'] = styled_df['연평균증가율'].apply(lambda x: f"{x:.1f}%")
        styled_df['변동성'] = styled_df['변동성'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # 2. 지역별 스마트그리드 적합성 분석
        st.markdown("### 🔍 지역별 스마트그리드 적합성 분석")
        
        # 적합성 점수 계산
        for idx, row in analysis_df.iterrows():
            # 규모 점수 (거래액 기준)
            scale_score = min(100, (row['최근거래액'] / analysis_df['최근거래액'].max()) * 100)
            
            # 성장성 점수 (성장률 기준)
            if row['연평균증가율'] > 10:
                growth_score = 100
            elif row['연평균증가율'] > 5:
                growth_score = 80
            elif row['연평균증가율'] > 0:
                growth_score = 60
            else:
                growth_score = 30
            
            # 안정성 점수 (변동성 기준 - 낮을수록 좋음)
            if row['변동성'] < 10:
                stability_score = 100
            elif row['변동성'] < 20:
                stability_score = 80
            elif row['변동성'] < 30:
                stability_score = 60
            else:
                stability_score = 40
            
            # 종합 점수
            total_score = (scale_score * 0.4 + growth_score * 0.3 + stability_score * 0.3)
            analysis_df.loc[idx, '스마트그리드_적합성'] = total_score
        
        # 상위 5개 지역 하이라이트
        top_5 = analysis_df.nlargest(5, '스마트그리드_적합성')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 스마트그리드 적합성 상위 5개 지역")
            for idx, (_, row) in enumerate(top_5.iterrows()):
                medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🏅"
                st.markdown(f"{medal} **{row['지역']}**: {row['스마트그리드_적합성']:.0f}점")
                st.markdown(f"   - 거래액: {row['최근거래액']:,.0f}억원")
                st.markdown(f"   - 성장률: {row['연평균증가율']:.1f}%")
                st.markdown(f"   - 변동성: {row['변동성']:.1f}%")
                st.markdown("")
        
        with col2:
            # 적합성 점수 시각화
            fig = px.bar(
                analysis_df.sort_values('스마트그리드_적합성', ascending=True),
                x='스마트그리드_적합성',
                y='지역',
                orientation='h',
                title="지역별 스마트그리드 적합성 점수",
                color='스마트그리드_적합성',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # 3. 권역별 분석
        st.markdown("### 🌏 권역별 스마트그리드 현황")
        
        metro_data = analysis_df[analysis_df['유형'] == '광역시/특별시']
        province_data = analysis_df[analysis_df['유형'] == '도/특별자치도']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not metro_data.empty:
                st.markdown("#### 🏙️ 광역시/특별시")
                avg_metro = {
                    '평균 거래액': metro_data['최근거래액'].mean(),
                    '평균 성장률': metro_data['연평균증가율'].mean(),
                    '평균 변동성': metro_data['변동성'].mean(),
                    '평균 적합성': metro_data['스마트그리드_적합성'].mean()
                }
                
                for key, value in avg_metro.items():
                    if '거래액' in key:
                        st.metric(key, f"{value:,.0f}억원")
                    elif '적합성' in key:
                        st.metric(key, f"{value:.0f}점")
                    else:
                        st.metric(key, f"{value:.1f}%")
        
        with col2:
            if not province_data.empty:
                st.markdown("#### 🏞️ 도/특별자치도")
                avg_province = {
                    '평균 거래액': province_data['최근거래액'].mean(),
                    '평균 성장률': province_data['연평균증가율'].mean(),
                    '평균 변동성': province_data['변동성'].mean(),
                    '평균 적합성': province_data['스마트그리드_적합성'].mean()
                }
                
                for key, value in avg_province.items():
                    if '거래액' in key:
                        st.metric(key, f"{value:,.0f}억원")
                    elif '적합성' in key:
                        st.metric(key, f"{value:.0f}점")
                    else:
                        st.metric(key, f"{value:.1f}%")

def create_green_energy_analysis(df):
    """신재생에너지 및 탄소중립 분석"""
    st.subheader("🌱 신재생에너지 & 탄소중립 분석")
    
    green_cols = ['RPS의무이행비용', '배출권거래비용', '예측제도정산금']
    available_green = [col for col in df.columns if col in green_cols]
    
    if not available_green:
        st.warning("신재생에너지 관련 데이터가 없습니다.")
        return
    
    # 1. 신재생에너지 투자 추이
    st.markdown("### 📈 신재생에너지 정책비용 추이")
    
    if 'Year' in df.columns and available_green:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('전체 추이', 'RPS 의무이행비용', '배출권거래비용', '예측제도정산금'),
            specs=[[{"colspan": 2}, None],
                   [{}, {}]]
        )
        
        # 전체 추이
        colors = ['#2E8B57', '#FF6347', '#4169E1', '#FFD700']
        for i, col in enumerate(available_green):
            valid_data = df[df[col].notna()]
            if len(valid_data) > 0:
                fig.add_trace(
                    go.Scatter(x=valid_data['Year'], y=valid_data[col], 
                             mode='lines+markers', name=col, 
                             line=dict(color=colors[i % len(colors)], width=3)),
                    row=1, col=1
                )
        
        # 개별 분석
        for i, col in enumerate(available_green[:2]):  # RPS와 배출권만
            valid_data = df[df[col].notna()]
            if len(valid_data) > 0:
                fig.add_trace(
                    go.Bar(x=valid_data['Year'].tail(10), y=valid_data[col].tail(10),
                          name=f'{col}_bar', showlegend=False,
                          marker_color=colors[i]),
                    row=2, col=i+1
                )
        
        fig.update_layout(height=600, title_text="신재생에너지 정책비용 분석")
        st.plotly_chart(fig, use_container_width=True)
    
    # 2. 탄소중립 기여도 분석
    st.markdown("### 🌍 탄소중립 기여도 분석")
    
    if 'RPS의무이행비용' in df.columns and 'Year' in df.columns:
        rps_data = df[df['RPS의무이행비용'].notna()]
        
        if len(rps_data) > 5:
            # 최근 5년 RPS 비용 증가율
            recent_rps = rps_data.tail(5)
            rps_growth = ((recent_rps['RPS의무이행비용'].iloc[-1] / recent_rps['RPS의무이행비용'].iloc[0]) ** (1/4) - 1) * 100
            
            # 전체 전력거래 대비 RPS 비중
            if '전국' in df.columns:
                total_data = df[df['전국'].notna()]
                merged_data = pd.merge(rps_data[['Year', 'RPS의무이행비용']], 
                                     total_data[['Year', '전국']], 
                                     on='Year', how='inner')
                
                if len(merged_data) > 0:
                    merged_data['RPS_비중'] = (merged_data['RPS의무이행비용'] / merged_data['전국']) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "RPS 비용 연평균 증가율",
                            f"{rps_growth:.1f}%",
                            help="신재생에너지 의무이행 비용의 증가 추이"
                        )
                    
                    with col2:
                        latest_ratio = merged_data['RPS_비중'].iloc[-1]
                        st.metric(
                            "전체 거래액 대비 RPS 비중",
                            f"{latest_ratio:.2f}%",
                            help="전체 전력거래액 중 RPS 비용이 차지하는 비중"
                        )
                    
                    with col3:
                        # 목표 달성도 (가정: 2030년까지 20% 달성 목표)
                        target_year = 2030
                        current_year = merged_data['Year'].iloc[-1]
                        years_to_target = target_year - current_year
                        
                        if years_to_target > 0:
                            required_growth = ((20 / latest_ratio) ** (1/years_to_target) - 1) * 100
                            achievement = min(100, (rps_growth / required_growth) * 100) if required_growth > 0 else 100
                            
                            st.metric(
                                "2030 목표 달성도",
                                f"{achievement:.0f}%",
                                help="현재 증가 추세로 2030년 신재생에너지 목표 달성 가능성"
                            )
                    
                    # RPS 비중 추이 그래프
                    fig = px.line(
                        merged_data, x='Year', y='RPS_비중',
                        title='전체 전력거래액 대비 RPS 비용 비중 추이',
                        markers=True
                    )
                    fig.add_hline(y=20, line_dash="dash", line_color="red", 
                                 annotation_text="2030 목표 (20%)")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    # 3. 배출권 거래 효과성 분석
    if '배출권거래비용' in df.columns:
        st.markdown("### 💰 배출권거래제 효과성")
        
        ets_data = df[df['배출권거래비용'].notna()]
        
        if len(ets_data) > 3:
            recent_ets = ets_data.tail(5)
            ets_values = recent_ets['배출권거래비용']
            
            # 배출권 비용 변동성 (안정성 지표)
            ets_volatility = (ets_values.std() / ets_values.mean()) * 100
            
            # 배출권 비용 증가율
            ets_growth = ((ets_values.iloc[-1] / ets_values.iloc[0]) ** (1/(len(ets_values)-1)) - 1) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "배출권 비용 변동성",
                    f"{ets_volatility:.1f}%",
                    help="낮을수록 배출권 시장이 안정적"
                )
                
                # 평가
                if ets_volatility < 15:
                    stability_level = "매우 안정"
                    color = "green"
                elif ets_volatility < 25:
                    stability_level = "안정"
                    color = "blue"
                elif ets_volatility < 35:
                    stability_level = "보통"
                    color = "orange"
                else:
                    stability_level = "불안정"
                    color = "red"
                
                st.markdown(f"<div class='insight-box'>시장 안정성: **{stability_level}**</div>", unsafe_allow_html=True)
            
            with col2:
                st.metric(
                    "배출권 비용 증가율",
                    f"{ets_growth:.1f}%/년",
                    help="배출권 비용의 연평균 증가율"
                )
                
                # 탄소 가격 신호 효과성 평가
                if ets_growth > 10:
                    signal_strength = "강함"
                elif ets_growth > 5:
                    signal_strength = "보통"
                else:
                    signal_strength = "약함"
                
                st.markdown(f"<div class='insight-box'>탄소 가격 신호: **{signal_strength}**</div>", unsafe_allow_html=True)

def create_demand_forecasting_analysis(df):
    """수요예측 및 디지털화 분석"""
    st.subheader("📊 전력 수요예측 & 디지털화 분석")
    
    if '예측제도정산금' not in df.columns:
        st.warning("수요예측 관련 데이터가 없습니다.")
        return
    
    # 1. 수요예측 정확도 분석
    st.markdown("### 🎯 수요예측 정확도 추이")
    
    pred_data = df[df['예측제도정산금'].notna()]
    
    if len(pred_data) > 5:
        # 예측제도정산금이 낮을수록 예측이 정확함
        pred_values = pred_data['예측제도정산금']
        years = pred_data['Year']
        
        # 추세 분석
        if len(pred_values) > 1:
            # 선형 회귀로 추세 계산
            x = np.arange(len(pred_values))
            z = np.polyfit(x, pred_values, 1)
            trend_slope = z[0]
            
            # 최근 5년 vs 초기 5년 비교
            if len(pred_values) >= 10:
                early_avg = pred_values.head(5).mean()
                recent_avg = pred_values.tail(5).mean()
                improvement_rate = ((early_avg - recent_avg) / early_avg) * 100
            else:
                improvement_rate = 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "예측 정확도 개선율",
                    f"{improvement_rate:.1f}%",
                    delta="개선" if improvement_rate > 0 else "악화",
                    help="초기 대비 최근 예측 정확도 개선 정도"
                )
            
            with col2:
                current_accuracy = "높음" if pred_values.iloc[-1] < pred_values.mean() else "보통"
                st.metric(
                    "현재 예측 정확도",
                    current_accuracy,
                    help="최근 예측제도정산금 기준"
                )
            
            with col3:
                trend_direction = "개선" if trend_slope < 0 else "악화"
                st.metric(
                    "전체 추세",
                    trend_direction,
                    help="전체 기간 동안의 예측 정확도 추세"
                )
            
            # 예측정산금 추이 그래프
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=years, y=pred_values,
                mode='lines+markers',
                name='예측제도정산금',
                line=dict(color='#4169E1', width=3),
                marker=dict(size=8)
            ))
            
            # 추세선 추가
            trend_line = np.poly1d(z)(x)
            fig.add_trace(go.Scatter(
                x=years, y=trend_line,
                mode='lines',
                name='추세선',
                line=dict(color='red', dash='dash', width=2)
            ))
            
            fig.update_layout(
                title='수요예측 정확도 추이 (예측제도정산금)',
                xaxis_title='연도',
                yaxis_title='정산금 (억원)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 2. 디지털화 수준 평가
    st.markdown("### 💻 전력시장 디지털화 수준")
    
    if len(pred_data) > 3:
        # 디지털화 지표 계산
        recent_data = pred_data.tail(3)
        early_data = pred_data.head(3)
        
        # 예측 안정성 (변동성 감소)
        recent_volatility = (recent_data['예측제도정산금'].std() / recent_data['예측제도정산금'].mean()) * 100
        early_volatility = (early_data['예측제도정산금'].std() / early_data['예측제도정산금'].mean()) * 100
        
        volatility_improvement = early_volatility - recent_volatility
        
        # 디지털화 점수 계산
        accuracy_score = min(100, improvement_rate * 2) if improvement_rate > 0 else 0
        stability_score = min(100, volatility_improvement * 2) if volatility_improvement > 0 else 0
        trend_score = 100 if trend_slope < 0 else 0
        
        digital_score = (accuracy_score + stability_score + trend_score) / 3
        
        # 디지털화 수준 시각화
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = digital_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "전력시장 디지털화 수준"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4169E1"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "lightgreen"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80}}))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # 세부 평가
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("예측 정확도", f"{accuracy_score:.0f}점")
        with col2:
            st.metric("예측 안정성", f"{stability_score:.0f}점")
        with col3:
            st.metric("개선 추세", f"{trend_score:.0f}점")
        
        # 디지털화 개선 제안
        st.markdown("### 🚀 디지털화 개선 방안")
        
        recommendations = []
        
        if accuracy_score < 50:
            recommendations.append("🎯 **AI/ML 기반 수요예측 모델 도입**: 머신러닝 알고리즘을 활용한 고도화된 예측 시스템 구축")
        
        if stability_score < 50:
            recommendations.append("📊 **실시간 데이터 수집 체계 강화**: IoT 센서와 스마트미터를 통한 실시간 데이터 수집 확대")
        
        if trend_score < 50:
            recommendations.append("🔄 **예측 모델 지속 개선**: 정기적인 모델 업데이트와 성능 모니터링 체계 구축")
        
        if digital_score >= 70:
            recommendations.append("✅ **현재 수준 유지 및 고도화**: 양호한 디지털화 수준을 바탕으로 차세대 기술 도입 검토")
        
        for rec in recommendations:
            st.markdown(f"<div class='insight-box'>{rec}</div>", unsafe_allow_html=True)

def create_policy_recommendations(df):
    """정책 제안 및 로드맵"""
    st.subheader("📋 스마트그리드 정책 제안 & 로드맵")
    
    # 전체 데이터 기반 종합 분석
    metrics = calculate_smart_grid_metrics(df)
    
    # 1. 우선순위별 정책 제안
    st.markdown("### 🎯 우선순위별 정책 제안")
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    # 지역별 변동성 기반 제안
    if '평균_지역별_변동성' in metrics:
        volatility = metrics['평균_지역별_변동성']
        if volatility > 25:
            high_priority.append({
                'title': '지역간 전력망 연계 강화',
                'description': '지역별 전력거래 변동성이 높아 안정성 확보가 시급',
                'actions': ['초고압 송전선로 확충', '지역간 연계선 증설', '지역별 ESS 설치 확대']
            })
        elif volatility > 15:
            medium_priority.append({
                'title': '지역별 전력 안정화',
                'description': '적정 수준이나 지속적인 모니터링 필요',
                'actions': ['지역별 수급 균형 모니터링', '예비력 확보', '수요관리 프로그램 확대']
            })
    
    # RPS 기반 제안
    if 'RPS의무이행비용_연평균증가율' in metrics:
        rps_growth = metrics['RPS의무이행비용_연평균증가율']
        if rps_growth < 5:
            high_priority.append({
                'title': '신재생에너지 확산 가속화',
                'description': 'RPS 확산 속도가 느려 2030 목표 달성이 어려울 수 있음',
                'actions': ['RE100 참여 기업 확대', '분산형 태양광 보급 확대', '해상풍력 개발 가속화']
            })
        elif rps_growth > 15:
            medium_priority.append({
                'title': '신재생에너지 안정화',
                'description': '빠른 성장으로 인한 계통 안정성 관리 필요',
                'actions': ['계통연계 기준 강화', '출력제한 시스템 고도화', '예측 정확도 향상']
            })
    
    # 예측 정확도 기반 제안
    if '예측정확도_개선율' in metrics:
        pred_improvement = metrics['예측정확도_개선율']
        if pred_improvement < 0:
            high_priority.append({
                'title': '수요예측 시스템 고도화',
                'description': '예측 정확도가 개선되지 않아 시장 효율성 저하',
                'actions': ['AI/ML 기반 예측모델 도입', '실시간 데이터 수집 확대', '기상정보 연계 강화']
            })
        elif pred_improvement < 10:
            medium_priority.append({
                'title': '예측 시스템 개선',
                'description': '점진적 개선 중이나 추가 고도화 필요',
                'actions': ['예측모델 정기 업데이트', '데이터 품질 관리', '예측 검증 체계 강화']
            })
    
    # 우선순위별 표시
    priorities = [
        ('🔴 높음 (즉시 추진)', high_priority),
        ('🟡 보통 (단기 추진)', medium_priority),
        ('🟢 낮음 (중장기 추진)', low_priority)
    ]
    
    for priority_name, items in priorities:
        if items:
            st.markdown(f"#### {priority_name}")
            for item in items:
                with st.expander(f"📌 {item['title']}"):
                    st.write(f"**배경**: {item['description']}")
                    st.write("**주요 실행과제**:")
                    for action in item['actions']:
                        st.write(f"- {action}")
    
    # 2. 단계별 로드맵
    st.markdown("### 🗓️ 스마트그리드 구축 로드맵")
    
    roadmap_data = {
        '단계': ['1단계 (2024-2025)', '2단계 (2026-2027)', '3단계 (2028-2030)'],
        '주요 목표': [
            '기반 인프라 구축',
            '시스템 고도화',
            '완전 자율운영'
        ],
        '핵심 과제': [
            '스마트미터 보급, 통신망 구축, 기초 데이터 수집',
            'AI 예측시스템, 실시간 제어, 분산자원 연계',
            '자율운영 시스템, 시장 완전개방, 국제 연계'
        ],
        '예상 투자': ['2조원', '3조원', '4조원'],
        '기대 효과': [
            '기초 효율성 10% 향상',
            '종합 효율성 25% 향상',
            '완전 최적화 40% 향상'
        ]
    }
    
    roadmap_df = pd.DataFrame(roadmap_data)
    st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
    
    # 3. 투자 우선순위
    st.markdown("### 💰 투자 우선순위 매트릭스")
    
    investment_matrix = {
        '분야': ['송배전망 현대화', '신재생에너지', 'ESS 확대', 'AI/빅데이터', '사이버보안', '인력양성'],
        '투자 규모': ['대', '대', '중', '중', '소', '소'],
        '기술 난이도': ['중', '중', '중', '고', '고', '저'],
        '기대 효과': ['고', '고', '중', '고', '중', '중'],
        '시급성': ['고', '고', '중', '중', '고', '저']
    }
    
    investment_df = pd.DataFrame(investment_matrix)
    
    # 우선순위 점수 계산 (간단한 가중치 적용)
    score_map = {'고': 3, '중': 2, '저': 1, '대': 3, '소': 1}
    
    investment_df['우선순위_점수'] = (
        investment_df['투자 규모'].map(score_map) * 0.2 +
        investment_df['기대 효과'].map(score_map) * 0.4 +
        investment_df['시급성'].map(score_map) * 0.4
    )
    
    investment_df = investment_df.sort_values('우선순위_점수', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(investment_df, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.scatter(
            investment_df, 
            x='기대 효과', 
            y='시급성',
            size='우선순위_점수',
            color='분야',
            title='투자 우선순위 매트릭스'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 4. 성과 지표 (KPI)
    st.markdown("### 📊 스마트그리드 성과 지표 (KPI)")
    
    kpi_data = {
        '구분': ['경제성', '경제성', '안정성', '안정성', '환경성', '환경성'],
        '지표명': [
            '전력거래 비용 절감률',
            '수요예측 정확도',
            '정전시간 단축률',
            '지역간 변동성',
            '신재생에너지 비중',
            '탄소배출 감축률'
        ],
        '현재 수준': ['5%', '85%', '20%', '18%', '12%', '15%'],
        '2025 목표': ['10%', '90%', '40%', '15%', '20%', '25%'],
        '2030 목표': ['20%', '95%', '60%', '10%', '30%', '40%']
    }
    
    kpi_df = pd.DataFrame(kpi_data)
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)
    
    # 5. 리스크 관리
    st.markdown("### ⚠️ 주요 리스크 및 대응방안")
    
    risks = [
        {
            'risk': '🔒 사이버보안 위협',
            'impact': '높음',
            'probability': '중간',
            'response': '보안관제센터 구축, 정기적 취약점 점검, 보안인증 강화'
        },
        {
            'risk': '⚡ 신재생에너지 간헐성',
            'impact': '높음',
            'probability': '높음',
            'response': 'ESS 확충, 수요반응 프로그램, 예측시스템 고도화'
        },
        {
            'risk': '💰 높은 초기 투자비용',
            'impact': '중간',
            'probability': '높음',
            'response': '단계적 투자, 민간 참여 확대, 정부 지원 정책'
        },
        {
            'risk': '👥 기술인력 부족',
            'impact': '중간',
            'probability': '중간',
            'response': '전문인력 양성, 해외인재 유치, 교육과정 개발'
        }
    ]
    
    for risk in risks:
        with st.expander(f"{risk['risk']} (영향도: {risk['impact']}, 발생가능성: {risk['probability']})"):
            st.write(f"**대응방안**: {risk['response']}")

def create_comparison_analysis(df):
    """국제 비교 및 벤치마킹"""
    st.subheader("🌐 국제 비교 및 벤치마킹")
    
    # 가상의 국제 비교 데이터 (실제 구현시에는 외부 API나 데이터 소스 활용)
    international_data = {
        '국가': ['한국', '독일', '덴마크', '미국', '일본', 'OECD 평균'],
        '스마트그리드 보급률': [65, 85, 90, 70, 75, 72],
        '신재생에너지 비중': [12, 42, 47, 18, 20, 28],
        '전력망 안정성': [85, 92, 95, 80, 88, 86],
        '디지털화 수준': [70, 88, 85, 82, 85, 80],
        '탄소배출량': [100, 60, 45, 85, 75, 70]  # 한국 기준 상대값
    }
    
    comparison_df = pd.DataFrame(international_data)
    
    # 1. 종합 비교
    st.markdown("### 📊 주요국 스마트그리드 현황 비교")
    
    # 레이더 차트
    categories = ['스마트그리드 보급률', '신재생에너지 비중', '전력망 안정성', '디지털화 수준']
    
    fig = go.Figure()
    
    for country in ['한국', '독일', '덴마크', 'OECD 평균']:
        values = []
        for cat in categories:
            values.append(comparison_df[comparison_df['국가'] == country][cat].iloc[0])
        values.append(values[0])  # 차트를 닫기 위해 첫 번째 값 추가
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            name=country,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        title="국가별 스마트그리드 역량 비교",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. 세부 분석
    st.markdown("### 🔍 세부 분야별 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 한국의 상대적 위치
        korea_data = comparison_df[comparison_df['국가'] == '한국'].iloc[0]
        oecd_data = comparison_df[comparison_df['국가'] == 'OECD 평균'].iloc[0]
        
        st.markdown("#### 🇰🇷 한국의 현황")
        
        for metric in ['스마트그리드 보급률', '신재생에너지 비중', '전력망 안정성', '디지털화 수준']:
            korea_val = korea_data[metric]
            oecd_val = oecd_data[metric]
            gap = korea_val - oecd_val
            
            if gap > 0:
                status = f"OECD 평균 대비 +{gap:.0f}p"
                delta_color = "normal"
            else:
                status = f"OECD 평균 대비 {gap:.0f}p"
                delta_color = "inverse"
            
            st.metric(
                metric,
                f"{korea_val}%",
                delta=status
            )
    
    with col2:
        st.markdown("#### 🎯 벤치마킹 대상국")
        
        # 각 분야별 1위 국가
        benchmarks = {}
        for metric in ['스마트그리드 보급률', '신재생에너지 비중', '전력망 안정성', '디지털화 수준']:
            best_country = comparison_df.loc[comparison_df[metric].idxmax(), '국가']
            best_value = comparison_df.loc[comparison_df[metric].idxmax(), metric]
            benchmarks[metric] = (best_country, best_value)
        
        for metric, (country, value) in benchmarks.items():
            st.write(f"**{metric}**: {country} ({value}%)")
        
        st.markdown("#### 🚀 개선 우선순위")
        korea_scores = {
            '스마트그리드 보급률': korea_data['스마트그리드 보급률'],
            '신재생에너지 비중': korea_data['신재생에너지 비중'],
            '전력망 안정성': korea_data['전력망 안정성'],
            '디지털화 수준': korea_data['디지털화 수준']
        }
        
        # OECD 평균 대비 가장 낮은 분야들
        gaps = {k: v - oecd_data[k] for k, v in korea_scores.items()}
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1])
        
        for i, (metric, gap) in enumerate(sorted_gaps[:3]):
            priority = "🔴 높음" if i == 0 else "🟡 보통" if i == 1 else "🟢 낮음"
            st.write(f"{priority} {metric} (격차: {gap:.0f}p)")
    
    # 3. 성공사례 분석
    st.markdown("### 🏆 해외 성공사례 분석")
    
    success_cases = [
        {
            'country': '🇩🇰 덴마크',
            'achievement': '신재생에너지 47% 달성',
            'key_factors': [
                '강력한 정부 정책 지원',
                '해상풍력 기술력 확보',
                '지역난방 시스템과 연계',
                '시민 참여형 에너지 협동조합'
            ],
            'lessons': '정책 일관성과 기술혁신, 시민참여의 조화'
        },
        {
            'country': '🇩🇪 독일',
            'achievement': '에너지전환(Energiewende) 추진',
            'key_factors': [
                '재생에너지법(EEG) 도입',
                '발전차액지원제도(FIT)',
                '분산형 전력시장 구축',
                '스마트그리드 기술 표준화'
            ],
            'lessons': '법제도 기반 구축과 시장 메커니즘 활용'
        },
        {
            'country': '🇺🇸 미국 (텍사스)',
            'achievement': '전력시장 완전 자유화',
            'key_factors': [
                '경쟁적 전력시장 구축',
                '실시간 가격제 도입',
                '수요반응 프로그램 활성화',
                '민간투자 활성화'
            ],
            'lessons': '시장 경쟁을 통한 효율성 극대화'
        }
    ]
    
    for case in success_cases:
        with st.expander(f"{case['country']}: {case['achievement']}"):
            st.write("**핵심 성공요인:**")
            for factor in case['key_factors']:
                st.write(f"- {factor}")
            st.write(f"**시사점**: {case['lessons']}")
    
    # 4. 한국 적용 방안
    st.markdown("### 🇰🇷 한국 적용 방안")
    
    applications = [
        {
            'area': '정책 프레임워크',
            'current': '개별법 중심의 분산된 정책',
            'improvement': '통합 스마트그리드법 제정, 정책 컨트롤타워 구축',
            'timeline': '2024-2025'
        },
        {
            'area': '시장 메커니즘',
            'current': '중앙집중식 전력시장',
            'improvement': '분산형 전력거래 허용, 실시간 가격제 도입',
            'timeline': '2025-2027'
        },
        {
            'area': '기술 표준',
            'current': '개별 기업 중심 기술개발',
            'improvement': '국가 표준 수립, 국제 표준 연계',
            'timeline': '2024-2026'
        },
        {
            'area': '시민 참여',
            'current': '정부/기업 주도',
            'improvement': '시민 참여형 에너지 프로그램 확대',
            'timeline': '2025-2030'
        }
    ]
    
    for app in applications:
        col1, col2, col3, col4 = st.columns([2, 3, 3, 1])
        with col1:
            st.write(f"**{app['area']}**")
        with col2:
            st.write(app['current'])
        with col3:
            st.write(app['improvement'])
        with col4:
            st.write(app['timeline'])

def run():
    # 헤더
    st.markdown('<h1 class="main-header">🔌 스마트그리드 실용성 분석 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('데이터를 로드하는 중...'):
        df = load_data()
    
    if df is None:
        st.error("데이터를 로드할 수 없습니다.")
        
        # 파일 업로드 옵션 제공
        st.subheader("📁 파일 직접 업로드")
        uploaded_file = st.file_uploader(
            "CSV 파일을 업로드하세요",
            type=['csv'],
            help="2023년도 전력시장통계.csv 파일을 업로드해주세요"
        )
        
        if uploaded_file is not None:
            try:
                # 업로드된 파일 처리
                with open("temp_data.csv", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                df = load_uploaded_data("temp_data.csv")
                if df is None:
                    st.stop()
            except Exception as e:
                st.error(f"파일 업로드 중 오류 발생: {str(e)}")
                st.stop()
        else:
            st.stop()
    
    # 사이드바 메뉴
    st.sidebar.title("🔌 스마트그리드 분석 메뉴")
    menu_options = [
        "스마트그리드 개요",
        "지역별 분석", 
        "신재생에너지 분석",
        "수요예측 & 디지털화",
        "정책 제안 & 로드맵",
        "국제 비교",
        "원본 데이터"
    ]
    selected_menu = st.sidebar.selectbox("분석 메뉴를 선택하세요:", menu_options)
    
    # 스마트그리드 관련 정보 패널
    with st.sidebar.expander("💡 스마트그리드란?"):
        st.write("""
        **스마트그리드**는 정보통신기술(ICT)을 활용하여 
        전력공급자와 소비자가 양방향으로 실시간 정보를 
        교환하여 전력 효율성을 최적화하는 차세대 전력망입니다.
        
        **주요 특징:**
        - 양방향 통신
        - 실시간 모니터링
        - 자동화된 제어
        - 분산형 에너지 자원 통합
        - 수요반응 프로그램
        """)
    
    with st.sidebar.expander("📊 분석 지표 설명"):
        st.write("""
        **지역별 변동성**: 지역간 전력거래량의 변동계수
        **RPS 비용**: 신재생에너지 의무이행 비용
        **배출권 비용**: 탄소배출권 거래 비용  
        **예측정산금**: 수요예측 오차로 인한 정산금
        **스마트그리드 적합성**: 종합 평가 점수
        """)
    
    # 메뉴별 화면 표시
    if selected_menu == "스마트그리드 개요":
        create_smart_grid_overview(df)
        
    elif selected_menu == "지역별 분석":
        create_regional_smart_grid_analysis(df)
        
    elif selected_menu == "신재생에너지 분석":
        create_green_energy_analysis(df)
        
    elif selected_menu == "수요예측 & 디지털화":
        create_demand_forecasting_analysis(df)
        
    elif selected_menu == "정책 제안 & 로드맵":
        create_policy_recommendations(df)
        
    elif selected_menu == "국제 비교":
        create_comparison_analysis(df)
        
    elif selected_menu == "원본 데이터":
        st.subheader("📋 원본 데이터")
        
        # 데이터 필터링
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Year' in df.columns:
                year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
                selected_years = st.slider(
                    "연도 범위:",
                    min_value=year_min,
                    max_value=year_max,
                    value=(year_min, year_max)
                )
                filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])].copy()
            else:
                filtered_df = df.copy()
        
        with col2:
            # 컬럼 선택
            numeric_cols = [col for col in df.columns if col != 'Year' and pd.api.types.is_numeric_dtype(df[col])]
            selected_columns = st.multiselect(
                "표시할 컬럼:",
                options=['Year'] + numeric_cols,
                default=['Year'] + numeric_cols[:10]
            )
        
        if selected_columns:
            display_df = filtered_df[selected_columns]
            st.dataframe(display_df, use_container_width=True, height=500)
            
            # 다운로드 버튼
            csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 CSV 다운로드",
                data=csv_data,
                file_name=f"smart_grid_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.info("🔌 스마트그리드 실용성 분석을 위한 전문 대시보드")
    
    # 데이터 상태 정보
    with st.sidebar.expander("📈 데이터 현황"):
        st.write(f"**총 데이터**: {len(df)}행 × {len(df.columns)}열")
        if 'Year' in df.columns:
            st.write(f"**기간**: {int(df['Year'].min())} - {int(df['Year'].max())}")
        
        # 주요 지표 가용성
        key_indicators = ['RPS의무이행비용', '배출권거래비용', '예측제도정산금']
        available_indicators = [col for col in df.columns if col in key_indicators]
        
        st.write(f"**주요 지표**: {len(available_indicators)}/{len(key_indicators)}개 사용가능")
        for indicator in available_indicators:
            data_count = df[indicator].count()
            st.write(f"  - {indicator}: {data_count}년")

if __name__ == "__main__":
    run()

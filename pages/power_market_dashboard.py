import streamlit as st
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

@st.cache_data
def load_data():
    """기본 전력시장 데이터 로드"""
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
        
        # 2. 스마트그리드 연계 분석
        st.markdown("### 🔌 스마트그리드 연계 분석")
        
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
                🔄 점진적 스마트그리드 구축<br>
                📈 장기 계획 수립
                </div>
                """, unsafe_allow_html=True)

def create_integrated_analysis(df, hourly_df, rps_df):
    """통합 분석 (기존 데이터 + 신규 데이터)"""
    st.subheader("🔄 통합 스마트그리드 분석")
    
    # 1. 수요-공급 균형 분석
    st.markdown("### ⚖️ 수요-공급 균형 분석")
    
    if hourly_df is not None and rps_df is not None:
        # 최근 일일 평균 수요량 계산
        hour_cols = [col for col in hourly_df.columns if '시' in col]
        if hour_cols and not hourly_df.empty:
            recent_day = hourly_df.tail(1)
            daily_demand = recent_day[hour_cols].values[0]
            
            # 시간별 수요량
            max_demand = max(daily_demand)
            min_demand = min(daily_demand)
            avg_demand = np.mean(daily_demand)
            
            # RPS 설비 총 용량
            energy_sources = ['태양광', '풍력', '수력', '바이오', '폐기물', '조류', '연료전지', '석탄가스화']
            available_sources = [col for col in rps_df.columns if col in energy_sources]
            
            if available_sources:
                total_rps_capacity = sum(rps_df[source].sum() for source in available_sources)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("현재 최대수요", f"{max_demand:,.0f} MW")
                
                with col2:
                    st.metric("RPS 총용량", f"{total_rps_capacity:,.0f} MW")
                
                with col3:
                    supply_ratio = (total_rps_capacity / max_demand) * 100 if max_demand > 0 else 0
                    st.metric("RPS 공급비율", f"{supply_ratio:.1f}%")
                
                with col4:
                    capacity_factor = 30  # 신재생에너지 평균 이용률 가정 (30%)
                    actual_supply = total_rps_capacity * (capacity_factor / 100)
                    actual_ratio = (actual_supply / avg_demand) * 100 if avg_demand > 0 else 0
                    st.metric("실제 공급비율", f"{actual_ratio:.1f}%")

def run():
    # 헤더
    st.markdown('<h1 class="main-header">🔌 스마트그리드 실용성 분석 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('데이터를 로드하는 중...'):
        df = load_data()
        hourly_df = load_hourly_demand_data()
        rps_df = load_rps_facility_data()
    
    if df is None:
        st.error("기본 전력시장 데이터를 로드할 수 없습니다.")
        st.stop()
    
    # 사이드바 메뉴
    st.sidebar.title("🔌 스마트그리드 분석 메뉴")
    menu_options = [
        "스마트그리드 개요",
        "시간별 수요 패턴",
        "RPS 설비현황",
        "통합 분석",
        "원본 데이터"
    ]
    selected_menu = st.sidebar.selectbox("분석 메뉴를 선택하세요:", menu_options)
    
    # 데이터 로드 상태 표시
    st.sidebar.markdown("### 📊 데이터 로드 상태")
    
    data_status = [
        ("기본 전력시장 데이터", df is not None),
        ("시간별 수요 데이터", hourly_df is not None),
        ("RPS 설비 데이터", rps_df is not None)
    ]
    
    for data_name, is_loaded in data_status:
        status_icon = "✅" if is_loaded else "❌"
        st.sidebar.write(f"{status_icon} {data_name}")
    
    # 메뉴별 화면 표시
    if selected_menu == "스마트그리드 개요":
        create_smart_grid_overview(df)
        
    elif selected_menu == "시간별 수요 패턴":
        create_hourly_demand_analysis(hourly_df)
        
    elif selected_menu == "RPS 설비현황":
        create_rps_facility_analysis(rps_df)
        
    elif selected_menu == "통합 분석":
        create_integrated_analysis(df, hourly_df, rps_df)
        
    elif selected_menu == "원본 데이터":
        st.subheader("📋 원본 데이터")
        
        # 데이터셋 선택
        dataset_choice = st.selectbox(
            "확인할 데이터셋:",
            ["기본 전력시장 데이터", "시간별 수요 데이터", "RPS 설비 데이터"]
        )
        
        if dataset_choice == "기본 전력시장 데이터" and df is not None:
            st.dataframe(df, use_container_width=True, height=500)
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 CSV 다운로드",
                data=csv_data,
                file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif dataset_choice == "시간별 수요 데이터" and hourly_df is not None:
            st.dataframe(hourly_df, use_container_width=True, height=500)
            
            csv_data = hourly_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 시간별 수요 데이터 다운로드",
                data=csv_data,
                file_name=f"hourly_demand_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        elif dataset_choice == "RPS 설비 데이터" and rps_df is not None:
            st.dataframe(rps_df, use_container_width=True, height=500)
            
            csv_data = rps_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 RPS 설비 데이터 다운로드",
                data=csv_data,
                file_name=f"rps_facility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        else:
            st.warning("선택한 데이터셋을 사용할 수 없습니다.")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.info("🔌 스마트그리드 실용성 분석을 위한 전문 대시보드")

if __name__ == "__main__":
    run()

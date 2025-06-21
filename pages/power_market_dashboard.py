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
    page_title="전력시장 통계 대시보드",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
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
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_uploaded_data(file_path):
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
            '2023년도 전력시장통계.csv',  # 현재 디렉토리
            'pages/2023년도 전력시장통계.csv',  # pages 폴더 안
            './pages/2023년도 전력시장통계.csv',  # 상대 경로
            '../2023년도 전력시장통계.csv'  # 상위 디렉토리
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
            '전국': [50000 + i*2000 + np.random.randint(-2000, 2000) for i in range(len(years))]
        }
        
        df = pd.DataFrame(sample_data)
        st.info("샘플 데이터로 대시보드 기능을 테스트할 수 있습니다.")
        return df

def create_summary_metrics(df):
    """주요 지표 요약 생성"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="전체 데이터 수",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="컬럼 수",
            value=f"{len(df.columns)}",
            delta=None
        )
    
    with col3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'Year']
        st.metric(
            label="지역/항목 수",
            value=f"{len(numeric_cols)}",
            delta=None
        )
    
    with col4:
        if 'Year' in df.columns:
            year_range = f"{int(df['Year'].min())}-{int(df['Year'].max())}"
        else:
            year_range = "N/A"
        st.metric(
            label="연도 범위",
            value=year_range,
            delta=None
        )

def create_data_overview(df):
    """데이터 개요 섹션"""
    st.subheader("📊 데이터 개요")
    
    # 요약 지표
    create_summary_metrics(df)
    
    # 데이터 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**데이터 정보:**")
        if 'Year' in df.columns:
            st.write(f"- 연도 범위: {int(df['Year'].min())} ~ {int(df['Year'].max())}")
            st.write(f"- 총 {int(df['Year'].max()) - int(df['Year'].min()) + 1}년 간 데이터")
        
        # 지역별 컬럼 표시
        regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', 
                  '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주', '세종']
        
        available_regions = [col for col in df.columns if col in regions]
        st.write(f"- 포함된 지역: {len(available_regions)}개")
        
        if available_regions:
            st.write("**주요 지역:**")
            for region in available_regions[:8]:  # 처음 8개만 표시
                data_count = df[region].count()
                st.write(f"  • {region}: {data_count}개 데이터")
    
    with col2:
        st.write("**데이터 샘플:**")
        # Year와 주요 지역 몇 개만 표시
        display_cols = ['Year']
        numeric_cols = [col for col in df.columns if col != 'Year' and pd.api.types.is_numeric_dtype(df[col])]
        display_cols.extend(numeric_cols[:5])
        
        sample_df = df[display_cols].head(10)
        st.dataframe(sample_df, use_container_width=True)

def create_data_filter(df):
    """데이터 필터링 기능"""
    st.subheader("🔍 데이터 필터링")
    
    # 연도 필터링
    if 'Year' in df.columns:
        year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
        selected_years = st.slider(
            "연도 범위 선택:",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max)
        )
        filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])].copy()
    else:
        filtered_df = df.copy()
    
    # 컬럼 선택
    numeric_cols = [col for col in df.columns if col != 'Year' and pd.api.types.is_numeric_dtype(df[col])]
    
    # 기본 선택: Year + 데이터가 많은 상위 컬럼들
    data_counts = []
    for col in numeric_cols:
        count = df[col].count()
        if count > 0:
            data_counts.append((col, count))
    
    data_counts.sort(key=lambda x: x[1], reverse=True)
    default_cols = ['Year'] + [col[0] for col in data_counts[:8]]
    
    selected_columns = st.multiselect(
        "표시할 컬럼을 선택하세요:",
        options=['Year'] + numeric_cols,
        default=default_cols
    )
    
    if not selected_columns:
        st.warning("최소 하나의 컬럼을 선택해주세요.")
        return df[['Year'] + numeric_cols[:5]].head(50)
    
    filtered_df = filtered_df[selected_columns].copy()
    
    # 행 수 제한
    max_rows = st.slider("표시할 최대 행 수", 10, min(100, len(filtered_df)), 50)
    
    return filtered_df.head(max_rows)

def create_visualizations(df):
    """다양한 시각화 생성"""
    st.subheader("📈 데이터 시각화")
    
    # 수치형 컬럼 (Year 제외)
    numeric_cols = [col for col in df.columns if col != 'Year' and pd.api.types.is_numeric_dtype(df[col])]
    
    if len(numeric_cols) == 0:
        st.warning("시각화할 수치형 데이터가 없습니다.")
        return
    
    # 시각화 타입 선택
    viz_type = st.selectbox(
        "시각화 유형을 선택하세요:",
        ["시계열 그래프", "막대 그래프", "히스토그램", "박스 플롯", "상관관계 히트맵", "지역별 비교", "전체 현황"]
    )
    
    if viz_type == "시계열 그래프":
        # 데이터가 많은 컬럼들을 기본 선택
        data_counts = [(col, df[col].count()) for col in numeric_cols]
        data_counts.sort(key=lambda x: x[1], reverse=True)
        default_selection = [col[0] for col in data_counts[:5]]
        
        selected_cols = st.multiselect(
            "시각화할 컬럼들 선택:", 
            numeric_cols, 
            default=default_selection
        )
        
        if selected_cols and 'Year' in df.columns:
            fig = go.Figure()
            
            for col in selected_cols:
                valid_data = df[df[col].notna()]
                if len(valid_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=valid_data['Year'], 
                        y=valid_data[col], 
                        mode='lines+markers',
                        name=col,
                        line=dict(width=2),
                        connectgaps=False
                    ))
            
            fig.update_layout(
                title="연도별 추이",
                xaxis_title="연도",
                yaxis_title="금액 (억원)",
                hovermode='x unified',
                height=600,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "막대 그래프":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot and 'Year' in df.columns:
            valid_data = df[df[col_to_plot].notna()].copy()
            if len(valid_data) > 0:
                recent_data = valid_data.tail(min(15, len(valid_data)))
                fig = px.bar(recent_data, x='Year', y=col_to_plot, 
                            title=f"{col_to_plot} - 연도별 현황")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"{col_to_plot} 컬럼에 유효한 데이터가 없습니다.")
    
    elif viz_type == "히스토그램":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            valid_data = df[df[col_to_plot].notna()][col_to_plot]
            if len(valid_data) > 0:
                bins = st.slider("구간 수", 5, 25, 15)
                fig = px.histogram(x=valid_data, nbins=bins, 
                                 title=f"{col_to_plot} 분포")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "박스 플롯":
        data_counts = [(col, df[col].count()) for col in numeric_cols]
        data_counts.sort(key=lambda x: x[1], reverse=True)
        default_selection = [col[0] for col in data_counts[:6]]
        
        cols_to_plot = st.multiselect("시각화할 컬럼들 선택:", numeric_cols, 
                                    default=default_selection)
        if cols_to_plot:
            fig = go.Figure()
            for col in cols_to_plot:
                valid_data = df[df[col].notna()][col]
                if len(valid_data) > 0:
                    fig.add_trace(go.Box(y=valid_data, name=col))
            
            fig.update_layout(title="박스 플롯 비교", height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "상관관계 히트맵":
        if len(numeric_cols) > 1:
            data_counts = [(col, df[col].count()) for col in numeric_cols]
            data_counts.sort(key=lambda x: x[1], reverse=True)
            available_cols = [col[0] for col in data_counts if col[1] > 5]
            
            if len(available_cols) > 1:
                default_selection = available_cols[:8]
                corr_cols = st.multiselect("상관관계를 볼 컬럼들 선택:", available_cols, 
                                         default=default_selection)
                if len(corr_cols) > 1:
                    corr_data = df[corr_cols].dropna()
                    if len(corr_data) > 1:
                        corr_matrix = corr_data.corr()
                        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                                       title="상관관계 히트맵", 
                                       color_continuous_scale='RdBu_r')
                        fig.update_layout(height=600)
                        st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "지역별 비교":
        korean_regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', 
                         '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
        
        region_cols = [col for col in df.columns if col in korean_regions]
        
        if region_cols:
            data_counts = [(col, df[col].count()) for col in region_cols]
            data_counts.sort(key=lambda x: x[1], reverse=True)
            default_selection = [col[0] for col in data_counts[:8]]
            
            selected_regions = st.multiselect("비교할 지역들 선택:", region_cols, 
                                            default=default_selection)
            
            if selected_regions and 'Year' in df.columns:
                fig = go.Figure()
                
                for region in selected_regions:
                    valid_data = df[df[region].notna()]
                    if len(valid_data) > 0:
                        fig.add_trace(go.Scatter(
                            x=valid_data['Year'], 
                            y=valid_data[region], 
                            mode='lines+markers',
                            name=region,
                            line=dict(width=2),
                            connectgaps=False
                        ))
                
                fig.update_layout(
                    title="지역별 전력거래금액 비교",
                    xaxis_title="연도",
                    yaxis_title="금액 (억원)",
                    hovermode='x unified',
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지역별 데이터를 찾을 수 없습니다.")
    
    elif viz_type == "전체 현황":
        if '전국' in df.columns and 'Year' in df.columns:
            valid_data = df[df['전국'].notna()]
            
            if len(valid_data) > 0:
                fig = go.Figure()
                
                # 전국 총액 추이
                fig.add_trace(go.Scatter(
                    x=valid_data['Year'], 
                    y=valid_data['전국'], 
                    mode='lines+markers',
                    name='전국 총액',
                    line=dict(width=3, color='red'),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="전국 전력거래금액 총액 추이",
                    xaxis_title="연도",
                    yaxis_title="금액 (억원)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 최근 데이터 요약
                if len(valid_data) > 0:
                    latest_year = valid_data['Year'].max()
                    latest_total = valid_data[valid_data['Year'] == latest_year]['전국'].iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("최신 연도", f"{int(latest_year)}년")
                    with col2:
                        st.metric("최신 전국 총액", f"{latest_total:,.0f}억원")
                    with col3:
                        if len(valid_data) > 1:
                            prev_total = valid_data[valid_data['Year'] == latest_year-1]['전국']
                            if len(prev_total) > 0:
                                growth = ((latest_total / prev_total.iloc[0]) - 1) * 100
                                st.metric("전년 대비 증가율", f"{growth:.2f}%")

def create_statistics_section(df):
    """통계 분석 섹션"""
    st.subheader("📊 통계 분석")
    
    # 기본 통계 요약
    if st.checkbox("기본 통계 요약 보기"):
        st.write("**기술통계량:**")
        numeric_data = df.select_dtypes(include=[np.number])
        valid_cols = [col for col in numeric_data.columns if numeric_data[col].count() > 0]
        if valid_cols:
            st.dataframe(numeric_data[valid_cols].describe())
    
    # 개별 분석
    numeric_cols = [col for col in df.columns 
                   if col != 'Year' and pd.api.types.is_numeric_dtype(df[col]) and df[col].count() > 0]
    
    if numeric_cols:
        st.write("**개별 항목 분석:**")
        selected_col = st.selectbox("분석할 항목 선택:", numeric_cols)
        
        if selected_col:
            valid_data = df[df[selected_col].notna()]
            
            if len(valid_data) > 0:
                col1, col2, col3 = st.columns(3)
                
                values = valid_data[selected_col]
                
                with col1:
                    st.metric("평균", f"{values.mean():,.0f}억원")
                    st.metric("중앙값", f"{values.median():,.0f}억원")
                
                with col2:
                    st.metric("표준편차", f"{values.std():,.0f}억원")
                    st.metric("최솟값", f"{values.min():,.0f}억원")
                
                with col3:
                    st.metric("최댓값", f"{values.max():,.0f}억원")
                    st.metric("데이터 개수", f"{len(values):,}년")
                
                # 연평균 증가율
                if 'Year' in df.columns and len(valid_data) > 1:
                    yearly_data = valid_data[['Year', selected_col]].sort_values('Year')
                    if len(yearly_data) > 1:
                        first_val = yearly_data[selected_col].iloc[0]
                        last_val = yearly_data[selected_col].iloc[-1]
                        years = yearly_data['Year'].iloc[-1] - yearly_data['Year'].iloc[0]
                        
                        if first_val > 0 and years > 0:
                            growth_rate = ((last_val / first_val) ** (1/years) - 1) * 100
                            st.metric("연평균 증가율", f"{growth_rate:.2f}%")

def run():
    # 헤더
    st.markdown('<h1 class="main-header">⚡ 2023년 전력시장통계 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드 (GitHub에서 직접 로드)
    with st.spinner('GitHub에서 데이터를 로드하는 중...'):
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
    st.sidebar.title("📋 메뉴")
    menu_options = ["데이터 개요", "데이터 보기", "시각화", "통계 분석", "데이터 다운로드"]
    selected_menu = st.sidebar.selectbox("메뉴를 선택하세요:", menu_options)
    
    # 메뉴별 화면 표시
    if selected_menu == "데이터 개요":
        create_data_overview(df)
        
    elif selected_menu == "데이터 보기":
        st.subheader("📋 데이터 테이블")
        filtered_df = create_data_filter(df)
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
    elif selected_menu == "시각화":
        create_visualizations(df)
        
    elif selected_menu == "통계 분석":
        create_statistics_section(df)
        
    elif selected_menu == "데이터 다운로드":
        st.subheader("💾 데이터 다운로드")
        
        filtered_df = create_data_filter(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 CSV 파일로 다운로드",
                data=csv_data,
                file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            try:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='전력시장통계')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📊 Excel 파일로 다운로드",
                    data=excel_data,
                    file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.info("💡 Excel 다운로드를 위해 openpyxl 패키지 설치가 필요합니다.")
        
        # 데이터 미리보기
        st.write("**다운로드될 데이터 미리보기:**")
        st.dataframe(filtered_df.head(10), use_container_width=True)
        st.info(f"총 {len(filtered_df)}행의 데이터가 다운로드됩니다.")
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.info("💡 이 대시보드는 전력시장 통계 데이터를 분석하기 위해 제작되었습니다.")
    
    # 데이터 소스 정보
    with st.sidebar.expander("📋 데이터 정보"):
        st.write("**데이터 소스:** 2023년도 전력시장통계.csv")
        st.write(f"**로드된 데이터:** {len(df)}행 × {len(df.columns)}열")
        if 'Year' in df.columns:
            st.write(f"**연도 범위:** {int(df['Year'].min())} - {int(df['Year'].max())}")
        
        # 포함된 지역 정보
        korean_regions = ['경기', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', 
                         '경남', '경북', '전남', '전북', '충남', '충북', '강원', '제주']
        region_cols = [col for col in df.columns if col in korean_regions]
        if region_cols:
            st.write(f"**포함된 지역:** {len(region_cols)}개")
            st.write(", ".join(region_cols))
        
        # 기타 항목
        other_cols = [col for col in df.columns if col not in korean_regions + ['Year', '전국']]
        if other_cols:
            st.write(f"**기타 항목:** {len(other_cols)}개")

if __name__ == "__main__":
    run()

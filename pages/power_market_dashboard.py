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

# CSV 파일 경로 설정
CSV_FILE_PATH = '2023년도 전력시장통계.csv'

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    try:
        # 다양한 인코딩으로 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                # 모든 행을 읽되, 헤더는 없다고 가정
                df_raw = pd.read_csv(CSV_FILE_PATH, encoding=encoding, header=None)
                
                # 데이터가 시작되는 행 찾기 (연도로 시작하는 행)
                data_start_idx = None
                header_idx = None
                
                for idx, row in df_raw.iterrows():
                    # 첫 번째 컬럼이 연도인 행 찾기
                    if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip().isdigit() and len(str(row.iloc[0]).strip()) == 4:
                        data_start_idx = idx
                        break
                
                # 영어 헤더가 있는 행 찾기 (Gyeonggi가 포함된 행)
                for idx, row in df_raw.iterrows():
                    if idx < data_start_idx and any('Gyeonggi' in str(cell) for cell in row if pd.notna(cell)):
                        header_idx = idx
                        break
                
                if data_start_idx is not None:
                    # 헤더 설정
                    if header_idx is not None:
                        # 영어 헤더 사용
                        headers = df_raw.iloc[header_idx].fillna('').astype(str)
                        # 첫 번째 컬럼은 'Year'로 설정
                        headers.iloc[0] = 'Year'
                        # 빈 헤더는 Column_N으로 설정
                        for i, header in enumerate(headers):
                            if header.strip() == '' or header == 'nan':
                                headers.iloc[i] = f'Column_{i}'
                    else:
                        # 기본 헤더 생성
                        headers = [f'Column_{i}' for i in range(len(df_raw.columns))]
                        headers[0] = 'Year'
                    
                    # 실제 데이터 추출
                    df = df_raw.iloc[data_start_idx:].copy()
                    df.columns = headers
                    df = df.reset_index(drop=True)
                    
                    # 데이터 타입 변환
                    # Year 컬럼을 정수로 변환
                    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
                    
                    # 숫자형 컬럼들 처리 (쉼표 제거 후 숫자로 변환)
                    for col in df.columns[1:]:  # Year 컬럼 제외
                        if df[col].dtype == 'object':
                            # 쉼표와 공백 제거 후 숫자로 변환 시도
                            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 빈 행 제거
                    df = df.dropna(how='all')
                    
                    st.success(f"✅ 데이터 로드 성공! 인코딩: {encoding}")
                    break
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                st.warning(f"인코딩 {encoding} 실패: {str(e)}")
                continue
        
        if df is None:
            raise Exception("모든 인코딩 시도 실패")
            
    except FileNotFoundError:
        st.error(f"❌ CSV 파일을 찾을 수 없습니다: {CSV_FILE_PATH}")
        st.info("현재 디렉토리에 '2023년도 전력시장통계.csv' 파일이 있는지 확인해주세요.")
        st.stop()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
        st.stop()
    
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
        st.metric(
            label="수치형 컬럼",
            value=f"{len(numeric_cols)}",
            delta=None
        )
    
    with col4:
        year_range = f"{df['Year'].min():.0f}-{df['Year'].max():.0f}" if 'Year' in df.columns else "N/A"
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
    
    # 데이터 타입 정보
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**컬럼 정보:**")
        st.write(f"- 총 컬럼 수: {len(df.columns)}개")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.write(f"- 수치형 컬럼: {len(numeric_cols)}개")
        
        # 주요 컬럼 표시
        st.write("**주요 컬럼들:**")
        for i, col in enumerate(df.columns[:10]):  # 처음 10개만 표시
            st.write(f"- {col}")
        if len(df.columns) > 10:
            st.write(f"... 외 {len(df.columns) - 10}개")
    
    with col2:
        st.write("**데이터 품질:**")
        missing_cols = df.isnull().sum()
        missing_cols = missing_cols[missing_cols > 0].sort_values(ascending=False)
        if len(missing_cols) > 0:
            st.write("결측치가 있는 컬럼:")
            for col, count in missing_cols.head(5).items():
                percentage = (count / len(df)) * 100
                st.write(f"- {col}: {count}개 ({percentage:.1f}%)")
            if len(missing_cols) > 5:
                st.write(f"... 외 {len(missing_cols) - 5}개 컬럼")
        else:
            st.write("결측치가 없습니다! ✅")

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
    default_cols = ['Year'] if 'Year' in df.columns else []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    default_cols.extend(numeric_cols[:10])  # 처음 10개 수치형 컬럼 추가
    
    selected_columns = st.multiselect(
        "표시할 컬럼을 선택하세요:",
        options=df.columns.tolist(),
        default=default_cols
    )
    
    if not selected_columns:
        st.warning("최소 하나의 컬럼을 선택해주세요.")
        return df.head(100)
    
    filtered_df = filtered_df[selected_columns].copy()
    
    # 행 수 제한
    max_rows = st.slider("표시할 최대 행 수", 10, min(1000, len(filtered_df)), 100)
    
    return filtered_df.head(max_rows)

def create_visualizations(df):
    """다양한 시각화 생성"""
    st.subheader("📈 데이터 시각화")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'Year' in numeric_cols:
        numeric_cols.remove('Year')  # Year는 제외 (X축으로 주로 사용)
    
    if len(numeric_cols) == 0:
        st.warning("시각화할 수치형 데이터가 없습니다.")
        return
    
    # 시각화 타입 선택
    viz_type = st.selectbox(
        "시각화 유형을 선택하세요:",
        ["시계열 그래프", "막대 그래프", "히스토그램", "박스 플롯", "상관관계 히트맵", "산점도", "지역별 비교"]
    )
    
    if viz_type == "시계열 그래프":
        selected_cols = st.multiselect(
            "시각화할 컬럼들 선택:", 
            numeric_cols, 
            default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
        )
        
        if selected_cols and 'Year' in df.columns:
            fig = go.Figure()
            
            for col in selected_cols:
                fig.add_trace(go.Scatter(
                    x=df['Year'], 
                    y=df[col], 
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                title="연도별 추이",
                xaxis_title="연도",
                yaxis_title="값",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "막대 그래프":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot and 'Year' in df.columns:
            # 최근 10년 데이터만 표시
            recent_df = df.nlargest(10, 'Year')
            fig = px.bar(recent_df, x='Year', y=col_to_plot, 
                        title=f"{col_to_plot} - 최근 10년")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "히스토그램":
        col_to_plot = st.selectbox("시각화할 컬럼 선택:", numeric_cols)
        if col_to_plot:
            bins = st.slider("구간 수", 10, 50, 20)
            fig = px.histogram(df, x=col_to_plot, nbins=bins, 
                             title=f"{col_to_plot} 분포")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "박스 플롯":
        cols_to_plot = st.multiselect("시각화할 컬럼들 선택:", numeric_cols, 
                                    default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols)
        if cols_to_plot:
            fig = go.Figure()
            for col in cols_to_plot:
                fig.add_trace(go.Box(y=df[col], name=col))
            fig.update_layout(title="박스 플롯 비교")
            st.plotly_chart(fig, use_container_width=True)
    
    elif viz_type == "상관관계 히트맵":
        if len(numeric_cols) > 1:
            corr_cols = st.multiselect("상관관계를 볼 컬럼들 선택:", numeric_cols, 
                                     default=numeric_cols[:8] if len(numeric_cols) >= 8 else numeric_cols)
            if len(corr_cols) > 1:
                corr_matrix = df[corr_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                               title="상관관계 히트맵", 
                               color_continuous_scale='RdBu_r')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("상관관계 분석을 위해서는 최소 2개의 수치형 컬럼이 필요합니다.")
    
    elif viz_type == "산점도":
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X축 컬럼:", numeric_cols, key="scatter_x")
            with col2:
                y_col = st.selectbox("Y축 컬럼:", numeric_cols, key="scatter_y", 
                                   index=1 if len(numeric_cols) > 1 else 0)
            
            if x_col != y_col:
                fig = px.scatter(df, x=x_col, y=y_col, 
                               title=f"{x_col} vs {y_col}",
                               hover_data=['Year'] if 'Year' in df.columns else None)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("산점도를 위해서는 최소 2개의 수치형 컬럼이 필요합니다.")
    
    elif viz_type == "지역별 비교":
        # 지역명이 포함된 컬럼들 찾기
        region_cols = [col for col in df.columns if any(region in col for region in 
                      ['Gyeonggi', 'Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan'])]
        
        if region_cols:
            selected_regions = st.multiselect("비교할 지역들 선택:", region_cols, 
                                            default=region_cols[:5] if len(region_cols) >= 5 else region_cols)
            
            if selected_regions and 'Year' in df.columns:
                fig = go.Figure()
                
                for region in selected_regions:
                    fig.add_trace(go.Scatter(
                        x=df['Year'], 
                        y=df[region], 
                        mode='lines+markers',
                        name=region,
                        line=dict(width=2)
                    ))
                
                fig.update_layout(
                    title="지역별 비교",
                    xaxis_title="연도",
                    yaxis_title="값",
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지역 데이터를 찾을 수 없습니다.")

def create_statistics_section(df):
    """통계 분석 섹션"""
    st.subheader("📊 통계 분석")
    
    # 기본 통계 요약
    if st.checkbox("기본 통계 요약 보기"):
        st.write("**기술통계량:**")
        st.dataframe(df.describe())
    
    # 연도별 통계
    if 'Year' in df.columns:
        st.write("**연도별 주요 통계:**")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'Year' in numeric_cols:
            numeric_cols.remove('Year')
        
        if numeric_cols:
            selected_col = st.selectbox("분석할 컬럼 선택:", numeric_cols)
            
            if selected_col:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_val = df[selected_col].mean()
                    st.metric("전체 평균", f"{avg_val:,.2f}")
                    
                    median_val = df[selected_col].median()
                    st.metric("중앙값", f"{median_val:,.2f}")
                
                with col2:
                    std_val = df[selected_col].std()
                    st.metric("표준편차", f"{std_val:,.2f}")
                    
                    min_val = df[selected_col].min()
                    st.metric("최솟값", f"{min_val:,.2f}")
                
                with col3:
                    max_val = df[selected_col].max()
                    st.metric("최댓값", f"{max_val:,.2f}")
                    
                    # 연평균 증가율 계산
                    if len(df) > 1:
                        first_val = df[selected_col].iloc[0]
                        last_val = df[selected_col].iloc[-1]
                        years = len(df) - 1
                        if first_val > 0 and years > 0:
                            growth_rate = ((last_val / first_val) ** (1/years) - 1) * 100
                            st.metric("연평균 증가율", f"{growth_rate:.2f}%")

def run():
    # 헤더
    st.markdown('<h1 class="main-header">⚡ 2023년 전력시장통계 대시보드</h1>', unsafe_allow_html=True)
    
    # 데이터 로드
    with st.spinner('데이터를 로드하는 중...'):
        df = load_data()
    
    # 데이터 로드 성공 메시지
    st.success(f"✅ 데이터가 성공적으로 로드되었습니다! (총 {len(df):,}행, {len(df.columns)}열)")
    
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
        
        # 필터링된 데이터 다운로드
        filtered_df = create_data_filter(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV 다운로드
            csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')  # BOM 추가로 한글 깨짐 방지
            st.download_button(
                label="📄 CSV 파일로 다운로드",
                data=csv_data,
                file_name=f"power_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Excel에서 열 때 한글이 깨지지 않도록 UTF-8 BOM 인코딩 사용"
            )
        
        with col2:
            # Excel 다운로드 (openpyxl 사용)
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
                st.info("💡 Excel 다운로드를 위해 openpyxl 패키지 설치가 필요합니다.\n`pip install openpyxl`")
        
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
            st.write(f"**연도 범위:** {df['Year'].min():.0f} - {df['Year'].max():.0f}")
        st.write("**주요 지역:** 경기, 강원, 경남, 경북, 전남, 전북, 충남, 충북, 제주, 서울, 인천, 대전, 광주, 대구, 세종, 울산, 부산")

if __name__ == "__main__":
    run()

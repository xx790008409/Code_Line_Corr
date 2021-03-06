import numpy as np
import pandas as pd
from scipy import stats


# Pearson 相关系数的实现，给定特征和标签series，返回相关系数值
def pearson(feature, label):
    # 自己实现的pearson算法
    cov = feature.cov(label)  # 协方差
    std_x = feature.std()  # 标准差
    std_y = label.std()  # 标准差
    if abs(std_x * std_y) < 1e-5:
        return np.nan
    else:
        pearson_corr = cov / (std_x * std_y)  # 特征与标签的相关系数
        # pearson_corr = min(1., max(-1., pearson_corr))  # 限制结果范围区间为[-1, 1]
        return round(pearson_corr, 6)  # 浮点数精度不准

    # 调用stats实现的pearson
    # try:
    #     return stats.pearsonr(feature, label)[0]
    # except:
    #     return np.nan


# Spearman 相关系数的实现，给定特征和标签series，返回相关系数值
def spearman(feature, label):
    # 排名没有并列的情况
    # feature_rank = data[feature].rank()
    # label_rank = data[label].rank()
    # diff = feature_rank.sub(label_rank)
    # diff_square = diff.mul(diff)
    #
    # N = int(data[label].count())
    # spearman_corr = 1 - 6 * sum(diff_square) / (N * (N * N - 1))
    # print(feature + ":" + str(spearman_corr))

    # 排名有并列的情况
    feature_rank = feature.rank()
    label_rank = label.rank()

    cov = feature_rank.cov(label_rank)  # 协方差
    std_x = feature_rank.std()  # 标准差
    std_y = label_rank.std()  # 标准差
    # 分母为0，相关系数则为nan
    if abs(std_x * std_y) < 1e-5:
        return np.nan
    else:
        spearman_corr = cov / (std_x * std_y)  # 特征与标签的相关系数
        # spearman_corr = min(1., max(-1., spearman_corr))  # 限制结果范围区间为[-1, 1]
        return round(spearman_corr, 6)

    # 调用stats实现的spearman
    # try:
    #     return stats.spearmanr(feature, label)[0]
    # except:
    #     return np.nan


# 计算kendall相关系数接口
# Kendall 相关系数的实现，给定特征和标签series，返回相关系数值
def kendall(feature, label):
    x = np.array(feature)
    y = np.array(label)

    size = x.size
    perm = np.argsort(y)
    x, y = x[perm], y[perm]
    y = np.r_[True, y[1:] != y[:-1]].cumsum(dtype=np.intp)

    perm = np.argsort(x, kind='mergesort')
    x, y = x[perm], y[perm]
    x = np.r_[True, x[1:] != x[:-1]].cumsum(dtype=np.intp)

    dis = calc_dis(y)  # discordant pairs

    obs = np.r_[True, (x[1:] != x[:-1]) | (y[1:] != y[:-1]), True]
    cnt = np.diff(np.nonzero(obs)[0]).astype('int64', copy=False)

    ntie = (cnt * (cnt - 1) // 2).sum()
    xtie = count_tie(x)
    ytie = count_tie(y)

    tot = (size * (size - 1)) // 2

    # tot = con + dis + (xtie - ntie) + (ytie - ntie) + ntie
    #     = con + dis + xtie + ytie - ntie
    con_minus_dis = tot - xtie - ytie + ntie - 2 * dis
    tau = con_minus_dis / np.sqrt(tot - xtie) / np.sqrt(tot - ytie)

    # tau = min(1., max(-1., tau))
    return round(tau, 6)


# 计算kendall相关系数中的xtie，ytie
def count_tie(vector):
    cnt = np.bincount(vector).astype('int64', copy=False)
    cnt = cnt[cnt > 1]
    return (cnt * (cnt - 1) // 2).sum()


# 求逆序对
def mergeSortInversion(data, aux, low, high):
    if low >= high:
        return 0

    mid = low + (high - low) // 2
    # 递归调用过程
    leftCount = mergeSortInversion(data, aux, low, mid)
    rightCount = mergeSortInversion(data, aux, mid + 1, high)

    # merge 过程
    for index in range(low, high + 1):
        aux[index] = data[index]
    count = 0
    i = low
    j = mid + 1
    k = i
    while k <= high:
        if i > mid and j <= high:
            data[k] = aux[j]
            j += 1
        elif j > high and i <= mid:
            data[k] = aux[i]
            i += 1
        elif aux[i] <= aux[j]:
            data[k] = aux[i]
            i += 1
        elif aux[i] > aux[j]:
            data[k] = aux[j]
            j += 1
            count += mid - i + 1
        k += 1

    return leftCount + rightCount + count


# 计算kendall相关系数中的不一致对
def calc_dis(y):
    aux = [y[i] for i in range(len(y))]
    nSwap = mergeSortInversion(y, aux, 0, len(y) - 1)
    return nSwap


# 计算Ncf、Nuf、Ncs、Nus
# c表示cover，u表示uncover
# f表示failure，s表示success
def get_N_para(feature, label):
    # N = len(label)
    # success = feature[label==0]
    # failure = feature[label==1]
    #
    # Ncf = np.sum(failure)
    # Nuf = N - Ncf
    #
    # Ncs = np.sum(success)
    # Nus = N - Ncs
    feature = np.array(feature)
    label = np.array(label)
    Ncf = np.sum(feature[label == 1])
    Nuf = np.sum(label == 1) - Ncf

    Ncs = np.sum(feature[label == 0])
    Nus = np.sum(label == 0) - Ncs

    return Ncf, Nuf, Ncs, Nus


# @xiehuan实现的卡方检验
def chisq(feature, label):
    # 实际值
    obs = list(get_N_para(feature, label))

    # 计算理论值
    fail_ratio = np.sum(label) / len(label)
    success_ratio = 1 - fail_ratio

    cover = np.sum(feature)
    uncover = len(feature) - cover

    Ncf = cover * fail_ratio
    Nuf = uncover * fail_ratio
    Ncs = cover * success_ratio
    Nus = uncover * success_ratio
    exp = [Ncf, Nuf, Ncs, Nus]

    return 1 - stats.chisquare(obs, exp)[1]


# Dstar
def dstar(feature, label):
    Ncf, Nuf, Ncs, Nus = get_N_para(feature, label)
    try:
        return round(Ncf ** 2 / (Ncs + Nuf), 6)
    except:
        return 0.0


# Ochiai
def ochiai(feature, label):
    Ncf, Nuf, Ncs, Nus = get_N_para(feature, label)
    try:
        return round(Ncf / np.sqrt((Ncf + Nuf) * (Ncf + Ncs)), 6)
    except:
        return 0.0


# Barinel
def barinel(feature, label):
    Ncf, Nuf, Ncs, Nus = get_N_para(feature, label)
    try:
        return round(1 - Ncs / (Ncs + Ncf), 6)
    except:
        return 0.0


# 时间复杂度较高的kendall相关系数实现，已优化，暂不使用
def k(data):
    # # 计算分母所需参数
    # xtie = count_tie(list(data[feature]))  # n1
    # ytie = count_tie(list(data[label]))  # n2
    # size = len(data[feature])  # n
    # tot = size * (size - 1) // 2  # n0
    #
    # # 计算分子
    # # TODO: 优化计算concordant - discordant的算法，详见维基百科（已优化，见上面归并排序求逆序对）
    # # 时间复杂度O(m * n ^ 2)，数据量大的时候慢得有点让人难以忍受。。。
    # # m 为特征数量，n为数据量
    # feature_rank = data[feature].rank()
    # label_rank = data[label].rank()
    # dis = 0  # 分子所需参数，dis = concordant - discordant
    # for i in range(1, size):
    #     for j in range(0, i):
    #         dis = dis + \
    #               np.sign(feature_rank[i] - feature_rank[j]) * \
    #               np.sign(label_rank[i] - label_rank[j])
    # # 计算并输出结果
    # # 分母为0，相关系数则为nan
    # if abs(np.sqrt(tot - xtie) * np.sqrt(tot - ytie)) < 1e-5:
    #     corr_dict[feature] = 'nan'
    # else:
    #     kendall_corr = dis / (np.sqrt(tot - xtie) * np.sqrt(tot - ytie))
    #     kendall_corr = min(1., max(-1., kendall_corr))  # 限制结果范围区间为[-1, 1]
    #     corr_dict[feature] = kendall_corr
    return 0


"""
*****************************************
********以下算法由@yasuoman实现***********
*****************************************
"""

import math


# 标签只能为0和1,样本空间任意
# samle:n*m 的列表
# label:m*1 的列表
# 返回每个特征的fisher score值的一个列表
# eg:  sample = [[1,2,3],[1,0,1],[1,5,6]]
#     label = [1, 0, 1]
# return  lst=[nan, 1.8148148148148149, 1.8148148148148149]
def binary_fisher_score(sample, label):
    if len(sample) != len(label):
        print('Sample does not match label')
        exit()
    df1 = pd.DataFrame(sample)
    df2 = pd.DataFrame(label, columns=['label'])
    data = pd.concat([df1, df2], axis=1)  # 合并成为一个dataframe

    data0 = data[data.label == 0]  # 对标签分类，分成包含0和1的两个dataframe
    data1 = data[data.label == 1]
    n = len(label)  # 标签长度
    n1 = sum(label)  # 1类标签的个数
    n0 = n - n1  # 0类标签的个数
    lst = []  # 用于返回的列表
    features_list = list(data.columns)[:-1]
    for feature in features_list:

        # 算关于data0
        m0_feature_mean = data0[feature].mean()  # 0类标签在第m维上的均值
        # 0类在第m维上的sw
        m0_SW = sum((data0[feature] - m0_feature_mean) ** 2)
        # 算关于data1
        m1_feature_mean = data1[feature].mean()  # 1类标签在第m维上的均值
        # 1类在第m维上的sw
        m1_SW = sum((data1[feature] - m1_feature_mean) ** 2)
        # 算关于data
        m_all_feature_mean = data[feature].mean()  # 所有类标签在第m维上的均值

        m0_SB = n0 / n * (m0_feature_mean - m_all_feature_mean) ** 2
        m1_SB = n1 / n * (m1_feature_mean - m_all_feature_mean) ** 2
        # 计算SB
        m_SB = m1_SB + m0_SB
        # 计算SW
        m_SW = (m0_SW + m1_SW) / n
        if m_SW == 0:
            # 0/0类型也是返回nan
            m_fisher_score = np.nan
        else:
            # 计算Fisher score
            m_fisher_score = m_SB / m_SW
        # Fisher score值添加进列表
        lst.append(round(m_fisher_score, 6))

    return lst


# 针对标签样本都是二值(0和1)的互信息,label和sample是对称的
# eg:label=[0,1,0]   sample=[1,0,1]
# return 0.6365141682948128
def binary_mutula_information(label, sample):
    # 用字典来计数
    d = dict()
    # 统计其中00,01,10,11各自的个数
    binary_mi_score = 0.0
    label = np.asarray(label)
    sample = np.asarray(sample)
    if label.size != sample.size:
        print('error！input array length is not equal.')
        exit()

    # np.sum(label)/label.size表示1在label中的概率,
    # 前者就是0在label中的概率
    # 这里需要用总的数目减去1的数目再除以总的数目，提高精度
    x = [(label.size - np.sum(label)) / label.size, np.sum(label) / label.size]

    y = [(sample.size - np.sum(sample)) / sample.size, np.sum(sample) / sample.size]

    for i in range(label.size):
        if (label[i], sample[i]) in d:
            d[label[i], sample[i]] += 1
        else:
            d[label[i], sample[i]] = 1

    # 遍历字典，得到各自的px,py,pxy，并求和
    for key in d.keys():
        px = x[key[0]]
        py = y[key[1]]
        pxy = d[key] / label.size
        binary_mi_score = binary_mi_score + pxy * math.log(pxy / (px * py))

    return round(binary_mi_score, 6)


# 用斯特林公式来近似求伽马函数（卡方检验）
def getApproxGamma(n):
    RECIP_E = 0.36787944117144232159552377016147
    TWOPI = 6.283185307179586476925286766559
    d = 1.0 / (10.0 * n)
    d = 1.0 / ((12 * n) - d)
    d = (d + n) * RECIP_E
    d = math.pow(d, n)
    d = d * math.sqrt(TWOPI / n)
    return d


# 不完全伽马函数中需要调用的函数（卡方检验）
def KM(s, z):
    _sum = 1.0
    log_nom = math.log(1.0)
    log_denom = math.log(1.0)
    log_s = math.log(s)
    log_z = math.log(z)
    for i in range(1000):
        log_nom += log_z
        s = s + 1
        log_s = math.log(s)
        log_denom += log_s
        log_sum = log_nom - log_denom
        log_sum = float(log_sum)
        _sum += math.exp(log_sum)

    return _sum


# 不完全伽马函数，采用计算其log值（卡方检验）
def log_igf(s, z):
    if z < 0.0:
        return 0.0
    sc = float((math.log(z) * s) - z - math.log(s))
    k = float(KM(s, z))
    return math.log(k) + sc


# 卡方检验求p值
# dof是自由度，chi_squared为卡方值，该函数实现知道自由度和卡方值求p值
# 核心是用不完全伽马函数除以伽马函数，两者都采用近似函数求解
# 参见https://blog.csdn.net/idatamining/article/details/8565042
def chisqr2pValue(dof, chi_squared):
    dof = int(dof)
    chi_squared = float(chi_squared)
    if dof < 1 or chi_squared < 0:
        return 0.0
    k = float(dof) * 0.5
    v = chi_squared * 0.5
    # 自由度为2时
    if dof == 2:
        return math.exp(-1.0 * v)
    # 不完全伽马函数，采用计算其log值
    incompleteGamma = log_igf(k, v)
    # 如果过小或者无穷
    if incompleteGamma == float('-inf') or incompleteGamma == float('inf'):
        return 1e-14

    # 完全伽马函数，用斯特林公式近似
    gamma = float(math.log(getApproxGamma(k)))
    incompleteGamma = incompleteGamma - gamma
    if math.exp(incompleteGamma) > 1:
        return 1e-14
    pvalue = float(1.0 - math.exp(incompleteGamma))
    return pvalue


# 自己实现chisquare,参数为两个列表obs,exp，返回为包含卡方值和p值的列表
# eg:obs=[8,7,7] ,exp=[8,8,8]
# return [0.25, 0.8824969025845955]
def my_chisquare(obs, exp):
    # 将列表转化为numpy.ndarray类型
    obs = np.atleast_1d(np.asanyarray(obs))
    exp = np.atleast_1d(np.asanyarray(exp))
    if obs.size != exp.size:
        print('The size of the obs and the exp  array is not equal')
        exit()

    # 得到ndarray类型，得到各项的理论与观察的相对偏离距离，相加即为卡方值
    terms = (obs - exp) ** 2 / exp
    # 求得卡方值,numpy.float64类型
    stat = terms.sum(axis=0)
    # 计算obs,exp的维度
    num_obs = terms.size
    # 调用自己写的求p值的函数，得到p值
    p = round(chisqr2pValue(num_obs - 1, stat), 6)
    chisquare_list = []
    chisquare_list.append(stat)
    chisquare_list.append(p)
    return chisquare_list

def return_max_vals_from_hist(list_orig, len_vid, prec):
    piks = []
    for i in range(180):

        if list_orig[i] > prec*len_vid:
            piks.append(i)

    return piks


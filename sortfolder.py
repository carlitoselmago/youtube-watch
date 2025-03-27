import pygame
import random
import os
import time
from curiosity import curiosity
from helpers.helpers import *
import sys

# SETTINGS ::::::::::::::::::::::::::::::
source_folder = "thumbs"
dest_folder = "sorted"
group_number = 4  # must be 4 for 2x2 grid
GUI = True
GUI_speed = 130
# :::::::::::::::::::::::::::::::::::::::

cur = curiosity(savemodel=False)
files = read_files(source_folder)
random.shuffle(files)
sorted_img = []

# GUI setup
if GUI:
    pygame.init()
    screen_width, screen_height = 1280, 720
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    pygame.display.set_caption("Image Curiosity Sorter")
    clock = pygame.time.Clock()

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def scale_to_fit(img, max_w, max_h):
    w, h = img.get_size()
    ratio = min(max_w / w, max_h / h)
    return pygame.transform.smoothscale(img, (int(w * ratio), int(h * ratio)))

def get_grid_positions(rows, cols, padding=20):
    current_w, current_h = screen.get_width(), screen.get_height()
    cell_w = current_w // cols
    cell_h = current_h // rows
    positions = []
    for i in range(rows):
        for j in range(cols):
            x = j * cell_w + cell_w // 2
            y = i * cell_h + cell_h // 2
            positions.append((x, y))
    return positions

def animate_images_in(image_surfaces, target_positions):
    frames = GUI_speed
    start_offsets = [i * 50 for i in range(len(image_surfaces))]  # to stagger vertical offsets
    for frame in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        t = ease_out_cubic(frame / (frames - 1))
        screen.fill((0, 0, 0))
        for i, (surf, (tx, ty)) in enumerate(zip(image_surfaces, target_positions)):
            offset = start_offsets[i]
            y = screen.get_height() + offset + (ty - (screen.get_height() + offset)) * t
            rect = surf.get_rect(center=(tx, y))
            screen.blit(surf, rect)
        pygame.display.flip()
        clock.tick(60)

def fade_and_shrink_others(image_surfaces, target_positions, best_idx, mse_scores):
    max_mse = max(mse_scores)
    min_mse = min(mse_scores)
    norm_scores = [(s - min_mse) / (max_mse - min_mse + 1e-5) for s in mse_scores]

    frames = GUI_speed
    for frame in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        t = ease_out_cubic(frame / (frames - 1))
        screen.fill((0, 0, 0))
        for i, (surf, (x, y)) in enumerate(zip(image_surfaces, target_positions)):
            min_opacity = 0.1
            if i == best_idx:
                screen.blit(surf, surf.get_rect(center=(x, y)))
            else:
                alpha = int((1 - t) * (255 * max(norm_scores[i], min_opacity)))
                scale = 1 - t * (1 - max(norm_scores[i], min_opacity))
                shrink = pygame.transform.rotozoom(surf, 0, scale)
                shrink.set_alpha(alpha)
                rect = shrink.get_rect(center=(x, y))
                screen.blit(shrink, rect)
        pygame.display.flip()
        clock.tick(60)

def center_and_scale_up(best_surf, start_pos):
    frames = GUI_speed
    end_pos = (screen.get_width() // 2, screen.get_height() // 2)
    for frame in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        t = ease_out_cubic(frame / (frames - 1))
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
        scale = 1 + t * 0.5
        enlarged = pygame.transform.rotozoom(best_surf, 0, scale)
        rect = enlarged.get_rect(center=(x, y))
        screen.fill((0, 0, 0))
        screen.blit(enlarged, rect)
        pygame.display.flip()
        clock.tick(60)
    return enlarged

def animate_best_out(best_surf):
    frames = GUI_speed
    x = screen.get_width() // 2
    y0 = screen.get_height() // 2
    for frame in range(frames):
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        t = ease_out_cubic(frame / (frames - 1))
        y = y0 - t * screen.get_height()
        rect = best_surf.get_rect(center=(x, y))
        screen.fill((0, 0, 0))
        screen.blit(best_surf, rect)
        pygame.display.flip()
        clock.tick(60)

while len(files) > 0:
    group = []
    mse_scores = []
    image_surfaces = []

    if GUI:
        positions = get_grid_positions(2, 2)

    for i in range(group_number):
        files, img_uri = get_new_file(files)
        group.append(img_uri)

        if GUI:
            img = pygame.image.load(img_uri).convert_alpha()
            img = scale_to_fit(img, screen.get_width() // 2 - 40, screen.get_height() // 2 - 40)
            image_surfaces.append(img)

        image = cur.prepare_image(img_uri)
        mse = cur.predict_and_calculate_mse(image) * 1000
        mse_scores.append(mse)

    for img_uri in group:
        image = cur.prepare_image(img_uri)
        cur.update_model_with_new_image(image, 1)

    maxindex = mse_scores.index(max(mse_scores))
    sorted_indices = sorted(range(len(mse_scores)), key=lambda i: mse_scores[i], reverse=True)
    sorted_imgs = [group[i] for i in sorted_indices]
    best_image = sorted_imgs[0]

    if GUI:
        animate_images_in(image_surfaces, positions)
        fade_and_shrink_others(image_surfaces, positions, maxindex, mse_scores)
        best_surf_enlarged = center_and_scale_up(image_surfaces[maxindex], positions[maxindex])
        animate_best_out(best_surf_enlarged)
        pygame.time.delay(500)

    move_image(dest_folder, best_image)
    sorted_img.append(best_image)
    files = read_files(source_folder)

if GUI:
    pygame.quit()

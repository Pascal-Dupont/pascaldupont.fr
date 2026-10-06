<?php

return array (
  'front-header' => 
  array (
    'navigation' => 
    array (
      'props' => 
      array (
        'showTopBar' => false,
        'sticky' => true,
        'overlap' => true,
      ),
      'style' => 
      array (
        'padding' => 
        array (
          'top' => 
          array (
            'value' => 0,
          ),
        ),
      ),
    ),
    'logo' => 
    array (
      'props' => 
      array (
        'layoutType' => 'text',
      ),
    ),
    'header-menu' => 
    array (
      'props' => 
      array (
        'hoverEffect' => 
        array (
          'type' => 'bordered-active-item bordered-active-item--bottom',
          'group' => 
          array (
            'border' => 
            array (
              'transition' => 'effect-borders-grow grow-from-left',
            ),
          ),
        ),
      ),
    ),
    'hero' => 
    array (
      'props' => 
      array (
        'heroSection' => 
        array (
          'layout' => 'textOnly',
        ),
      ),
      'style' => 
      array (
        'descendants' => 
        array (
          'outer' => 
          array (
            'padding' => 
            array (
              'top' => 
              array (
                'value' => 150,
              ),
              'bottom' => 
              array (
                'value' => 150,
              ),
            ),
            'background' => 
            array (
              'overlay' => 
              array (
                'enabled' => true,
                'gradient_opacity' => 100,
              ),
              'type' => 'video',
            ),
          ),
        ),
      ),
      'full_height' => true,
      'hero_column_width' => 90,
    ),
    'buttons' => 
    array (
      'value' => 
      array (
        0 => 
        array (
          'label' => 'get in control',
        ),
        1 => 
        array (
          'label' => 'contact us',
        ),
      ),
    ),
  ),
  'header' => 
  array (
    'navigation' => 
    array (
      'props' => 
      array (
        'showTopBar' => false,
        'sticky' => true,
        'overlap' => true,
      ),
      'style' => 
      array (
        'padding' => 
        array (
          'top' => 
          array (
          ),
        ),
      ),
    ),
    'header-menu' => 
    array (
      'props' => 
      array (
        'hoverEffect' => 
        array (
          'type' => 'bordered-active-item bordered-active-item--bottom',
          'group' => 
          array (
            'border' => 
            array (
              'transition' => 'effect-borders-grow grow-from-left',
            ),
          ),
        ),
      ),
    ),
    'logo' => 
    array (
      'props' => 
      array (
        'layoutType' => 'text',
      ),
    ),
  ),
);

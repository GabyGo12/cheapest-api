import { Module } from '@nestjs/common';

// Repositories (Data Layer)
import {
  ItemInventarioRepository,
  RegistroCompraRepository,
  RegistroVentaRepository,
} from './repositories';

// Services
import {
  ItemInventarioService,
  RegistroCompraService,
  RegistroVentaService,
} from './services';

// Controllers
import {
  ItemInventarioController,
  RegistroCompraController,
  RegistroVentaController,
} from './controllers';

// Clients Mock
import { DatabaseModule } from '../datasources/database.module';
import { LogisticaModule } from '../logistica/logistica.module';
import { repositoryProviders } from './repositories/repository.providers';

import { IdentificacionModule } from '../identificacion/identificacion.module';

@Module({
  imports: [DatabaseModule, LogisticaModule, IdentificacionModule],
  controllers: [
    ItemInventarioController,
    RegistroVentaController,
    RegistroCompraController,
  ],
  providers: [
    // Repositories
    ...repositoryProviders,
    ItemInventarioRepository,
    RegistroVentaRepository,
    RegistroCompraRepository,
    // Services
    ItemInventarioService,
    RegistroVentaService,
    RegistroCompraService,
   
  ],
  exports: [ItemInventarioService, RegistroVentaService, RegistroCompraService],
})
export class InventarioModule {}
